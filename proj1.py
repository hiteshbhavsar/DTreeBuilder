import random
import math

# Each tree node consists of:
#   1. a vector list => [([feature vector], class), ..]
#   2. the selected attribute to split the vector list
#   3. its children => {selected attribute value : node, ..}
class node:
    def __init__(self):
        self.vecs = list()
        self.attr_split = None
        self.children = dict()


# function to read data file
# parameter: data file name or path to data file
# return: list of featre vectors and its corresponding class pair => [([feature_vector], class)..]
def read_file(filename):
    fea_vecs = []
    file = open(filename, "r")
    for line in file:
        values = line.split(",")
        fea_vecs.append((values[:6], values[6].replace("\n", "")))
    return fea_vecs


feature_vecs = []
attributes = ["White King file", " White King rank", "White Rook file", "White Rook rank", "Black King file", "Black King rank"]
feature_vecs = read_file("550-p1-cset-krk-1.csv")

Training_Set = []
Holdout_Set= []
Validation_Set = []


def sets_generator():
    total_data = len(feature_vecs)
    data_indexes = list(range(total_data))

    total_training_set_data = int(total_data * (.60));
    remaining_data = total_data - total_training_set_data

    if remaining_data % 2 == 1:
        total_training_set_data += 1
        remaining_data - 1

    Training_indexes = random.sample(data_indexes, total_training_set_data)

    for element in Training_indexes:
        Training_Set.append(feature_vecs[element])
        data_indexes.remove(element)


    Holdout_indexes = random.sample(data_indexes, int(remaining_data/2))

    for element in Holdout_indexes:
        Holdout_Set.append(feature_vecs[element])
        data_indexes.remove(element);


    Validation_indexes = list(data_indexes);

    for element in Validation_indexes:
        Validation_Set.append(feature_vecs[element])
        data_indexes.remove(element)


def entropy(class_occurrence, total):
    node_entropy = 0
    for minwindepth in class_occurrence:
        class_probability = class_occurrence[minwindepth] / total
        node_entropy += -class_probability*math.log(class_probability,2)
    return node_entropy


# Formula to find information gain
def FindInfoGain(entropy_set,entropy_attr,probab):
    return entropy_set-sum([entropy_attr[i]*probab[i] for i in range(len(entropy_attr))])


# Select best attribut to split a node
# Take as input a tree node
# When finish, tree node's property is modified accordingly
def split_node(root, attrs):
    # Calculate root entropy
    class_occurrence = dict()
    for pair in root.vecs:
        if pair[1] in class_occurrence:
            class_occurrence[pair[1]] += 1
        else:
            class_occurrence[pair[1]] = 1
    total = len(root.vecs)
    root_ent = entropy(class_occurrence, total)
    print("root entropy:", root_ent)

    # Calculate average entropy for each attribute value
    info_gain = list()
    for i in range(len(root.vecs[0][0])):
        class_occurence = dict()
        total = dict()
        for pair in root.vecs:
            if pair[0][i] not in class_occurence:
                class_occurence[pair[0][i]] = dict()
                total[pair[0][i]] = 1
            else:
                total[pair[0][i]] += 1
            if pair[1] in class_occurence[pair[0][i]]:
                class_occurence[pair[0][i]][pair[1]] += 1
            else:
                class_occurence[pair[0][i]][pair[1]] = 1
        entropy_list = list()
        for attr_val in class_occurence:
            entropy_list.append((total[attr_val], entropy(class_occurence[attr_val], total[attr_val])))
        avg_ent = 0
        for ent in entropy_list:
            avg_ent += ent[0] / len(root.vecs) * ent[1]
        info_gain.append(avg_ent)
        print("Attribute " + attrs[i] + "'s average entropy:", avg_ent)

    # Calculate information gain for each attribute
    print()
    max_info = (0, 0)
    for i in range(len(info_gain)):
        info_gain[i] = root_ent - info_gain[i]
        if info_gain[i] > max_info[1]:
            max_info = (i, info_gain[i])
        print("Attribute " + attrs[i] + "'s information gain:", info_gain[i])
    print("Attribute " + attrs[max_info[0]] + " has the greatest information gain, so it is selected as the attribute to split\n")

    # Updatte root node properties
    root.attr_split = max_info[0]
    for pair in root.vecs:
        if pair[0][root.attr_split] not in root.children:
            root.children[pair[0][root.attr_split]] = node()
        root.children[pair[0][root.attr_split]].vecs.append(pair)

# check whether a node is a leaf node
def isLeaf(root):
    pair1 = root.vecs[0][1]
    for pair in root.vecs:
        if pair[1] != pair1:
            return False
    return True

# build a decision tree using the provided root node
def buildDTree(root):
    queue = [root]
    while len(queue) > 0:
        curr = queue.pop(0)
        split_node(curr, attributes)
        for child in curr.children:
            if not isLeaf(curr.children[child]):
                queue.append(curr.children[child])

# classified the provided vector using the provided rooted tree
def classifier(root, feat_vec):
    curr = root
    while not isLeaf(curr):
        if feat_vec[0][curr.attr_split] in curr.children:
            curr = curr.children[feat_vec[0][curr.attr_split]]
        else:
            class_occurence = dict()
            for pair in curr.vecs:
                if pair[1] in class_occurence:
                    class_occurence[pair[1]] += 1
                else:
                    class_occurence[pair[1]] = 1
            max = (0, "")
            for c in class_occurence:
                if class_occurence[c] > max[0]:
                    max = (class_occurence[c], c)
            return max[1]

    return curr.vecs[0][1]


def accuracy(tree_root, v_set):
    correct = 0;
    incorrect_indexes = []
    i = 0
    for pair in v_set:
        if (classifier(tree_root, pair) == pair[1]):
            correct += 1
        else:
            incorrect_indexes.append(i)
        i += 1
    return correct / len(v_set), incorrect_indexes


def bagging_replacement(root, t_set, holdout_set):
    union_set = t_set + holdout_set
    final_t_set = []
    final_holdout_set = []

    for i in accuracy(root, holdout_set)[1]:
        union_set.append(holdout_set[i])
        union_set.append(holdout_set[i])

    for i in t_set:
        add_index = random.randint(0, len(t_set) - 1)
        final_t_set.append(union_set[add_index])

    # remove duplicates before removing items in final_t_set
    for item in union_set:
        if item not in final_holdout_set:
            final_holdout_set.append(item)

    for item in final_t_set:
        if item in final_holdout_set:
            final_holdout_set.remove(item)

    return final_t_set, final_holdout_set


'''
attributes = ["crust size", "shape", "filling size"]
root = node()
root.vecs = [(["big", "circle", "small"], "pos"),(["small", "circle", "small"], "pos"),(["big", "square", "small"], "neg"),(["big", "triangle", "small"], "neg"),(["big", "square", "big"], "pos"),(["small", "square", "small"], "neg"),(["small", "square", "big"], "pos"),(["big", "circle", "big"], "pos")]
print("\n\nTest Data:\n", root.vecs, "\n\nAttributes:\n", attributes, "\n")
split_node(root, attributes)
print("\nAfter splitting:")
for child in root.children:
    print("Attribute " + child + " has vector list:\n", root.children[child].vecs, "\n")
'''

attributes = ["White King file", " White King rank", "White Rook file", "White Rook rank", "Black King file", "Black King rank"]
feature_vecs = read_file("550-p1-cset-krk-1.csv")

sets_generator()
print(len(feature_vecs))
print(len(Training_Set))
print(len(Holdout_Set))
print(len(Validation_Set))

root = node()
root.vecs = Training_Set
if not isLeaf(root): 
    buildDTree(root)

# print(classifier(root, Holdout_Set[5]))
print("Printing first dTree accuracy")
print(accuracy(root, Validation_Set)[0])

Training_Set, Holdout_Set = bagging_replacement(root, Training_Set, Holdout_Set)

root = node()
root.vecs = Training_Set
if not isLeaf(root):
    buildDTree(root)

print("Printing second dTree accuracy")
print(accuracy(root, Holdout_Set)[0])