from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
from pymongo import MongoClient
from backend.rule_engine import create_rule, combine_rules, evaluate_rule, reconstruct_ast
from backend.db import get_db

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}})


db = get_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    try:
        rule_string = request.json.get('rule_string')
        if not rule_string:
            return jsonify({"error": "Missing 'rule_string' in request"}), 400

        print(f"Received rule_string: {rule_string}")  

        ast_node = create_rule(rule_string)

        if ast_node is None:
            return jsonify({"error": "Failed to create AST from rule string"}), 400

        print(f"Created AST: {ast_node}")  

        
        db.rules.insert_one({"rule_string": rule_string, "ast": ast_node.to_dict()})
        return jsonify(ast_node.to_dict()), 201
    except Exception as e:
        print(f"Error in create_rule_api: {e}")  
        return jsonify({"error": str(e)}), 500


@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    try:
        rule_strings = request.json.get('rule_strings')
        if not rule_strings or not isinstance(rule_strings, list):
            return jsonify({"error": "Missing or invalid 'rule_strings' in request"}), 400

        print(f"Received rule_strings: {rule_strings}")  

        combined_ast = combine_rules(rule_strings)

        if combined_ast is None:
            return jsonify({"error": "Failed to combine rules"}), 400

        print(f"Combined AST: {combined_ast}") 

      
        db.combined_rules.insert_one({"rule_strings": rule_strings, "ast": combined_ast.to_dict()})
        return jsonify(combined_ast.to_dict()), 201
    except Exception as e:
        print(f"Error in combine_rules_api: {e}")  
        return jsonify({"error": str(e)}), 500


@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    try:
        ast_data = request.json.get('ast')
        user_data = request.json.get('user_data')

        if not ast_data or not user_data:
            return jsonify({"error": "Missing 'ast' or 'user_data' in request"}), 400

        print(f"Received ast: {ast_data}")        
        print(f"Received user_data: {user_data}") 

        
        ast_node = reconstruct_ast(ast_data)
        result = evaluate_rule(ast_node, user_data)

        return jsonify({"result": result}), 200
    except Exception as e:
        print(f"Error in evaluate_rule_api: {e}")  
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
