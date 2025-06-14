from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
from datetime import datetime

from config import Config
from gemini_client import GeminiClient

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 配置 CORS
import os
logger.info(f"环境变量 CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")
logger.info(f"CORS配置: {Config.CORS_ORIGINS}")
CORS(app, origins=Config.CORS_ORIGINS)

# 配置 SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins=Config.CORS_ORIGINS,
    async_mode='eventlet'
)

# 初始化 Gemini 客户端
try:
    gemini_client = GeminiClient()
    logger.info("Gemini 客户端初始化成功")
except Exception as e:
    logger.error(f"Gemini 客户端初始化失败：{str(e)}")
    gemini_client = None

# 存储对话历史
conversation_history = []

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gemini_available': gemini_client is not None,
        'config': {
            'environment': Config.FLASK_ENV,
            'debug': Config.DEBUG,
            'port': Config.PORT,
            'api_key_configured': bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here')
        }
    })

@app.route('/api/question', methods=['POST'])
def receive_question():
    """接收问题并生成回答"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': '缺少问题内容'}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({'error': '问题内容不能为空'}), 400
        
        logger.info(f"收到问题：{question}")
        
        # 检查是否需要生成回答（根据 generate_answer 参数）
        should_generate_answer = data.get('generate_answer', True)
        
        if should_generate_answer and gemini_client:
            # 生成 AI 回答
            answer = gemini_client.generate_answer(question)
            logger.info(f"生成回答：{answer[:100]}...")
        else:
            answer = None
            logger.info("跳过生成回答")
        
        # 创建对话记录
        conversation = {
            'id': len(conversation_history) + 1,
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'has_answer': answer is not None
        }
        
        # 保存到历史记录
        conversation_history.append(conversation)
        
        # 通过 WebSocket 推送给前端
        socketio.emit('new_conversation', conversation)
        
        return jsonify({
            'success': True,
            'conversation': conversation
        })
        
    except Exception as e:
        logger.error(f"处理问题时出错：{str(e)}")
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """获取所有对话历史"""
    return jsonify({
        'conversations': conversation_history,
        'total': len(conversation_history)
    })

@app.route('/api/conversations', methods=['DELETE'])
def clear_conversations():
    """清空所有对话历史"""
    try:
        global conversation_history
        conversation_history.clear()

        logger.info("对话历史已清空")

        # 通过WebSocket通知所有客户端
        socketio.emit('conversation_history', {
            'conversations': [],
            'total': 0
        })

        return jsonify({
            'success': True,
            'message': '对话历史已清空'
        })

    except Exception as e:
        logger.error(f"清空对话历史时出错：{str(e)}")
        return jsonify({'error': f'清空失败：{str(e)}'}), 500

@app.route('/api/reload-config', methods=['POST'])
def reload_config():
    """重新加载配置"""
    try:
        # 重新加载配置
        Config.reload()

        # 重新初始化Gemini客户端
        global gemini_client
        try:
            gemini_client = GeminiClient()
            logger.info("配置重载后，Gemini 客户端重新初始化成功")
        except Exception as e:
            logger.error(f"配置重载后，Gemini 客户端重新初始化失败：{str(e)}")
            gemini_client = None

        return jsonify({
            'success': True,
            'message': '配置重载成功',
            'config': {
                'environment': Config.FLASK_ENV,
                'debug': Config.DEBUG,
                'port': Config.PORT,
                'api_key_configured': bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here'),
                'gemini_available': gemini_client is not None
            }
        })

    except Exception as e:
        logger.error(f"重载配置时出错：{str(e)}")
        return jsonify({'error': f'重载配置失败：{str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """客户端连接时的处理"""
    logger.info(f"客户端已连接：{request.sid}")
    
    # 发送历史对话记录
    emit('conversation_history', {
        'conversations': conversation_history,
        'total': len(conversation_history)
    })

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接时的处理"""
    logger.info(f"客户端已断开：{request.sid}")

@socketio.on('request_answer')
def handle_request_answer(data):
    """处理前端请求生成回答"""
    try:
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            emit('error', {'message': '缺少对话 ID'})
            return
        
        # 查找对话记录
        conversation = None
        for conv in conversation_history:
            if conv['id'] == conversation_id:
                conversation = conv
                break
        
        if not conversation:
            emit('error', {'message': '对话记录不存在'})
            return
        
        if conversation['has_answer']:
            emit('error', {'message': '该问题已有回答'})
            return
        
        if not gemini_client:
            emit('error', {'message': 'Gemini 客户端未初始化'})
            return
        
        # 生成回答
        answer = gemini_client.generate_answer(conversation['question'])
        
        # 更新对话记录
        conversation['answer'] = answer
        conversation['has_answer'] = True
        
        # 推送更新
        socketio.emit('conversation_updated', conversation)
        
    except Exception as e:
        logger.error(f"生成回答时出错：{str(e)}")
        emit('error', {'message': f'生成回答失败：{str(e)}'})

if __name__ == '__main__':
    logger.info(f"启动服务器，地址：{Config.HOST}:{Config.PORT}")

    # 测试 Gemini 连接
    if gemini_client and gemini_client.test_connection():
        logger.info("Gemini API 连接测试成功")
    else:
        logger.warning("Gemini API 连接测试失败，请检查配置")

    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
