import ast
import operator
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ASTNode:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  
        self.left = left           
        self.right = right         
        self.value = value          

    def to_dict(self):
        return {
            "node_type": self.node_type,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "value": self.value
        }

    def __repr__(self):
        return f"ASTNode(type={self.node_type}, value={self.value})"

def create_rule(rule_string):
    try:
       
        assignment_match = re.match(r'^\s*\w+\s*=\s*(["\'])(.*)\1\s*$', rule_string, re.DOTALL)
        if assignment_match:
            
            rule_expression = assignment_match.group(2)
            logger.debug(f"Extracted rule expression from assignment: {rule_expression}")
        else:
            
            rule_expression = rule_string
            logger.debug("No assignment detected. Using entire string as rule expression.")

       
        rule_expression = rule_expression.replace("AND", "and").replace("OR", "or")

        
        rule_expression = re.sub(r'(?<![=!<>])=(?![=])', '==', rule_expression)
        logger.debug(f"Transformed rule string: {rule_expression}")

      
        parsed = ast.parse(rule_expression, mode='eval')
        return convert_ast_to_custom_ast(parsed.body)
    except Exception as e:
        logger.error(f"Error in create_rule: {e}")
        return None

def convert_ast_to_custom_ast(node):
    if isinstance(node, ast.BoolOp):
        operator_str = "AND" if isinstance(node.op, ast.And) else "OR"
        logger.debug(f"Processing BoolOp with operator: {operator_str}")
        
        
        if len(node.values) < 2:
            raise ValueError("BoolOp must have at least two values.")
        
      
        current_node = convert_ast_to_custom_ast(node.values[0])
        for value in node.values[1:]:
            current_node = ASTNode(
                node_type="operator",
                left=current_node,
                right=convert_ast_to_custom_ast(value),
                value=operator_str
            )
        return current_node
    elif isinstance(node, ast.Compare):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("Only simple comparisons are supported.")
        
        
        if isinstance(node.left, ast.Name):
            left = node.left.id
        else:
            raise ValueError("Left operand must be a field name.")
        
       
        operator_map = {
            ast.Gt: "Gt",
            ast.Lt: "Lt",
            ast.Eq: "Eq",
            ast.GtE: "GtE",
            ast.LtE: "LtE",
            ast.NotEq: "NotEq",
        }
        op_type = type(node.ops[0])
        operator_str = operator_map.get(op_type)
        if not operator_str:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        
        comparator = node.comparators[0]
        if isinstance(comparator, ast.Constant):  
            right = comparator.value
        elif isinstance(comparator, ast.Num):   
            right = comparator.n
        elif isinstance(comparator, ast.Str):     
            right = comparator.s
        else:
            raise ValueError("Unsupported comparator type.")
        
      
        if isinstance(right, str):
            right = f"'{right}'"
        
        logger.debug(f"Processing Compare: {left} {operator_str} {right}")
        
        return ASTNode(node_type="operand", value=f"{left} {operator_str} {right}")
    else:
        raise ValueError(f"Unsupported AST node type: {type(node).__name__}")

def combine_rules(rules):
    combined_root = None
    for rule in rules:
        rule_ast = create_rule(rule)
        if rule_ast is None:
            logger.warning(f"Skipping invalid rule: {rule}")
            continue
        if combined_root is None:
            combined_root = rule_ast
            logger.debug("Initialized combined AST with the first valid rule.")
        else:
            combined_root = ASTNode("operator", left=combined_root, right=rule_ast, value="OR")
            logger.debug("Combined AST updated with operator 'OR'.")
    if combined_root is None:
        logger.error("No valid rules to combine.")
    return combined_root

def evaluate_rule(ast_node, data):
    if ast_node.node_type == "operand":
        parts = ast_node.value.split(' ', 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid operand format: {ast_node.value}")
        
        field, operator_str, value = parts
        operators_map = {
            "Gt": operator.gt,
            "Lt": operator.lt,
            "Eq": operator.eq,
            "GtE": operator.ge,
            "LtE": operator.le,
            "NotEq": operator.ne,
        }
        op_func = operators_map.get(operator_str)
        if not op_func:
            raise ValueError(f"Unsupported operator: {operator_str}")
        
        if field not in data:
            raise ValueError(f"Missing field in user data: '{field}'")
        
        data_value = data.get(field)
        
       
        if isinstance(data_value, int):
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Expected integer for field '{field}', got '{value}'")
        elif isinstance(data_value, str):
            if value.startswith("'") and value.endswith("'"):
                value = value.strip("'")
            else:
                raise ValueError(f"Expected string for field '{field}', got '{value}'")
        else:
            raise ValueError(f"Unsupported data type for field '{field}': {type(data_value).__name__}")
        
        result = op_func(data_value, value)
        logger.debug(f"Evaluated operand: {data_value} {operator_str} {value} = {result}")
        return result
    elif ast_node.node_type == "operator":
        left_result = evaluate_rule(ast_node.left, data)
        right_result = evaluate_rule(ast_node.right, data)
        if ast_node.value == "AND":
            result = left_result and right_result
        elif ast_node.value == "OR":
            result = left_result or right_result
        else:
            raise ValueError(f"Unsupported logical operator: {ast_node.value}")
        logger.debug(f"Evaluated operator: {ast_node.value} with results {left_result} and {right_result} = {result}")
        return result
    else:
        raise ValueError(f"Unsupported AST node type: {ast_node.node_type}")

def reconstruct_ast(node_dict):
    if node_dict['node_type'] == 'operator':
        left = reconstruct_ast(node_dict['left']) if node_dict['left'] else None
        right = reconstruct_ast(node_dict['right']) if node_dict['right'] else None
        return ASTNode(node_type='operator', left=left, right=right, value=node_dict['value'])
    elif node_dict['node_type'] == 'operand':
        return ASTNode(node_type='operand', value=node_dict['value'])
    else:
        raise ValueError(f"Unsupported node_type: {node_dict['node_type']}")
