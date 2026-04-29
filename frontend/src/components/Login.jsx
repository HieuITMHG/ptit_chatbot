import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

import logoPtit from '../assets/logo-ptit.png';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const API_URL = import.meta.env.VITE_API_BASE_URL;

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post(`${API_URL}/login/`, formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                withCredentials: true 
            });

            if (response.data && response.data.access_token) {
                localStorage.setItem('access_token', response.data.access_token);
            }

            navigate('/chat');
        } catch (error) {
            console.error(error);
            alert('Đăng nhập thất bại! Vui lòng kiểm tra lại tài khoản.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-gray-200 p-4 font-sans">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden transform transition-all hover:shadow-red-100/50">
                
                {/* Header Section */}
                <div className="bg-white p-8 pb-4 text-center">
                    <img 
                        src={logoPtit} 
                        alt="PTIT Logo" 
                        className="h-24 mx-auto mb-4 object-contain"
                    />
                    <h2 className="text-2xl font-extrabold text-red-700 uppercase tracking-tight">
                        PTIT Chatbot AI
                    </h2>
                    <p className="text-gray-500 text-sm mt-1 font-medium italic">Hệ thống hỗ trợ sinh viên thông minh</p>
                </div>

                {/* Form Section */}
                <form onSubmit={handleLogin} className="p-8 pt-4">
                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">Tên đăng nhập</label>
                            <input
                                type="text"
                                required
                                placeholder="Mã số sinh viên / Email"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-gray-50/50 placeholder:text-gray-400"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">Mật khẩu</label>
                            <input
                                type="password"
                                required
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-gray-50/50 placeholder:text-gray-400"
                            />
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        disabled={isLoading}
                        className={`w-full mt-10 bg-red-600 text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-red-200 hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-300 transition-all transform active:scale-[0.98] flex justify-center items-center ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
                    >
                        {isLoading ? (
                            <svg className="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : null}
                        {isLoading ? 'Đang xác thực...' : 'Đăng nhập'}
                    </button>
                </form>

                {/* Footer Section */}
                <div className="bg-gray-50/80 p-5 border-t border-gray-100 text-center">
                    <p className="text-[11px] text-gray-500 font-semibold tracking-wide uppercase">
                        &copy; {new Date().getFullYear()} Học viện Công nghệ Bưu chính Viễn thông
                    </p>
                </div>
            </div>
        </div>
    );
}