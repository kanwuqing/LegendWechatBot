import difflib
import yaml

def load_tree_from_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config['TCM']['tree']

def find_most_similar_question(tree, user_input):
    def traverse_tree(tree, path=[]):
        questions = []
        for key, value in tree.items():
            if isinstance(value, dict):
                if 'q' in value:
                    questions.append((value['q'], path + [key]))
                questions.extend(traverse_tree(value, path + [key]))
        return questions

    questions = traverse_tree(tree)
    question_texts = [q[0] for q in questions]
    most_similar = difflib.get_close_matches(user_input, question_texts, n=1, cutoff=0.0)
    
    if most_similar:
        for question, path in questions:
            if question == most_similar[0]:
                return path, question
    return None, None

# 示例用法
tree = load_tree_from_yaml('config.yaml')
user_input = "我心烦"

path, question = find_most_similar_question(tree, user_input)
if path:
    print(f"最相似的问题是: '{question}'")
    print(f"所属的树路径是: {' -> '.join(path)}")
else:
    print("未找到相似的问题")