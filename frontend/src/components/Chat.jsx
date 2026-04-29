import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import logoPtit from '../assets/logo-ptit.png'; 

export default function Chat() {
    const [messages, setMessages] = useState([
        { text: "Chào bạn! Tôi là trợ lý ảo PTIT. Tôi có thể giúp gì cho bạn hôm nay?", sender: 'ai' }
    ]);
    const [input, setInput] = useState('');
    const [ws, setWs] = useState(null);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);
    const navigate = useNavigate();

    const WS_URL = import.meta.env.VITE_WS_BASE_URL;

    useEffect(() => {
        let token = localStorage.getItem('access_token');
        if (!token) {
            navigate('/');
            return;
        }

        const socket = new WebSocket(`${WS_URL}/ws/chat?token=${token}`);
        
        socket.onopen = () => console.log('Đã kết nối WebSocket');
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.status === 'Processing') {
                setIsTyping(true);
            } else if (data.status === 'Completed') {
                setIsTyping(false);
                
                try {
                    const parsedAnswer = JSON.parse(data.answer);
                    
                    const mainText = parsedAnswer.text_res;
                    
                    const sources = parsedAnswer.ref_source && parsedAnswer.ref_source.length > 0
                        ? "\n\n📌 Nguồn tham khảo:\n" + parsedAnswer.ref_source.map((src, idx) => `[${idx+1}] ${src}`).join('\n')
                        : "";

                    setMessages(prev => [...prev, { 
                        text: mainText + sources, 
                        sender: 'ai' 
                    }]);
                    
                } catch (e) {
                    setMessages(prev => [...prev, { text: data.answer, sender: 'ai' }]);
                }
            } else if (data.status === 'Error') {
                setIsTyping(false);
                alert("Lỗi: " + data.message);
            }
        };

        socket.onclose = (e) => {
            if (e.code === 1008) {
                localStorage.removeItem('access_token');
                navigate('/'); 
            }
        };

        setWs(socket);
        return () => socket.close();
    }, [navigate, WS_URL]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const sendMessage = (e) => {
        e.preventDefault();
        if (!input.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;

        setMessages(prev => [...prev, { text: input, sender: 'user' }]);
        ws.send(JSON.stringify({ prompt: input }));
        setInput('');
    };

    const handleLogout = async () => {
        const confirmLogout = window.confirm("Bạn có chắc chắn muốn đăng xuất?");
        if (!confirmLogout) return;

        try {

            await axios.post(`${import.meta.env.VITE_API_BASE_URL}/logout/`, {}, { 
                withCredentials: true 
            });
        } catch (error) {
            console.error("Lỗi khi gọi API logout:", error);
        } finally {

            localStorage.removeItem('access_token');
            
            navigate('/');
        }
    };

    return (
        <div className="flex h-screen bg-gray-100 font-sans">
            {/* Sidebar - Chỉ giữ Logo và Logout */}
            <div className="hidden md:flex w-20 lg:w-64 bg-red-800 text-white flex-col transition-all">
                <div className="p-6 border-b border-red-700">
                    <img src={logoPtit} alt="PTIT" className="h-10 lg:h-12 mx-auto brightness-0 invert" />
                    <p className="hidden lg:block text-center mt-2 text-[10px] font-bold uppercase tracking-[0.2em] opacity-70">
                        AI Assistant
                    </p>
                </div>
                
                <div className="flex-1 flex flex-col justify-end p-4">
                    <button 
                        onClick={handleLogout} 
                        className="flex items-center justify-center lg:justify-start space-x-3 p-3 w-full text-red-100 hover:bg-red-700 hover:text-white rounded-xl transition-all duration-200 group"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span className="hidden lg:block font-medium">Đăng xuất</span>
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-white md:bg-gray-50">
                {/* Header */}
                <header className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-red-200">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-base md:text-lg font-bold text-gray-800 leading-none">PTIT Chatbot AI</h1>
                            <div className="flex items-center mt-1">
                                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                                <span className="ml-2 text-[10px] text-green-600 font-bold uppercase tracking-wider">Trực tuyến</span>
                            </div>
                        </div>
                    </div>
                    {/* Nút logout nhỏ cho Mobile */}
                    <button onClick={handleLogout} className="md:hidden p-2 text-gray-400 hover:text-red-600">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                    </button>
                </header>

                {/* Messages List */}
                <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-fixed">
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                            <div className={`flex max-w-[85%] md:max-w-[70%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <div className={`flex-shrink-0 h-9 w-9 rounded-xl flex items-center justify-center text-xs font-bold shadow-sm ${
                                    msg.sender === 'user' ? 'ml-3 bg-blue-600 text-white' : 'mr-3 bg-red-600 text-white'
                                }`}>
                                    {msg.sender === 'user' ? 'BẠN' : 'AI'}
                                </div>
                                <div className={`px-4 py-3 shadow-md border ${
                                    msg.sender === 'user' 
                                    ? 'bg-blue-600 border-blue-500 text-white rounded-2xl rounded-tr-none' 
                                    : 'bg-white border-gray-100 text-gray-800 rounded-2xl rounded-tl-none'
                                }`}>
                                    <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex justify-start animate-fadeIn">
                            <div className="flex items-center bg-white border border-gray-100 px-5 py-4 rounded-2xl rounded-tl-none shadow-md ml-12">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </main>

                {/* Input Area */}
                <footer className="p-4 md:p-6 bg-white border-t">
                    <form onSubmit={sendMessage} className="max-w-4xl mx-auto flex items-center bg-gray-100 border border-gray-200 rounded-2xl px-4 py-1.5 focus-within:ring-2 focus-within:ring-red-500 focus-within:bg-white transition-all duration-200 shadow-sm">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Nhập câu hỏi của bạn tại đây..."
                            className="flex-1 bg-transparent py-3 outline-none text-gray-800 placeholder-gray-400 text-sm md:text-base"
                        />
                        <button 
                            type="submit" 
                            disabled={!input.trim() || !ws || ws.readyState !== WebSocket.OPEN}
                            className="ml-2 p-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:bg-gray-300 disabled:scale-100 transition-all shadow-lg shadow-red-100 active:scale-90"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 rotate-90" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                            </svg>
                        </button>
                    </form>
                    <p className="text-center text-[10px] text-gray-400 mt-3 font-medium tracking-wide">
                        &copy; {new Date().getFullYear()} PTIT AI ASSISTANT - DÀNH CHO SINH VIÊN P.T.I.T
                    </p>
                </footer>
            </div>
        </div>
    );
}