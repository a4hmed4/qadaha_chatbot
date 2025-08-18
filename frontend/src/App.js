import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Grid,
  Card,
  CardContent,
  Divider,
  Badge,
  Fade,
  Zoom,
  Slide
} from '@mui/material';
import {
  Send as SendIcon,
  School as SchoolIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  Lightbulb as LightbulbIcon,
  Book as BookIcon,
  Science as ScienceIcon,
  Calculate as CalculateIcon,
  EmojiEmotions as EmojiIcon,
  TrendingUp as TrendingIcon,
  Chat as ChatIcon,
  BarChart as BarChartIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import axios from 'axios';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

// دالة لتنسيق النص وتحويل النص المحاط بعلامات النجمة إلى نص عريض
const formatMessageText = (text) => {
  if (!text) return '';

  // معالجة النص على مرحلتين: أولاً ** ثم *
  // هذا يضمن أن النص المحاط بـ ** يتم معالجته قبل النص المحاط بـ *
  
  // المرحلة 1: معالجة النص المحاط بعلامتي نجمة (**)
  const doubleStar = /\*\*(.+?)\*\*/g;
  let processedText = text;
  const parts = [];
  let lastIndex = 0;
  let counter = 0;
  
  // تحويل النص إلى مصفوفة من العناصر العادية والعناصر المنسقة
  const processText = (inputText, regex, weight) => {
    const result = [];
    let lastIdx = 0;
    let m;
    
    while ((m = regex.exec(inputText)) !== null) {
      // إضافة النص العادي قبل العلامات
      if (m.index > lastIdx) {
        result.push(inputText.substring(lastIdx, m.index));
      }
      
      // إضافة النص المنسق
      result.push(
        <span key={`bold-${counter++}`} style={{ fontWeight: weight }}>
          {m[1]}
        </span>
      );
      
      lastIdx = m.index + m[0].length;
    }
    
    // إضافة أي نص متبقي
    if (lastIdx < inputText.length) {
      result.push(inputText.substring(lastIdx));
    }
    
    return result;
  };
  
  // معالجة النص المحاط بعلامتي نجمة أولاً (وزن 900)
  const boldParts = processText(text, doubleStar, 900);
  
  // معالجة النص المتبقي للبحث عن علامة نجمة واحدة
  const processedParts = [];
  
  for (const part of boldParts) {
    // إذا كان الجزء نصًا عاديًا (وليس عنصر React)، ابحث فيه عن علامات النجمة الفردية
    if (typeof part === 'string') {
      const singleStar = /\*([^*]+)\*/g;
      const regularParts = processText(part, singleStar, 700);
      processedParts.push(...regularParts);
    } else {
      // إذا كان الجزء منسقًا بالفعل، أضفه كما هو
      processedParts.push(part);
    }
  }
  
  return processedParts.length > 0 ? processedParts : text;
};

// إنشاء ثيم مخصص لمؤسسة قدها التعليمية
const theme = createTheme({
  palette: {
    primary: {
      main: '#1e40af', // أزرق غامق - لون مؤسسة قدها
      light: '#3b82f6',
      dark: '#1e3a8a',
    },
    secondary: {
      main: '#059669', // أخضر - لون التعليم
      light: '#10b981',
      dark: '#047857',
    },
    background: {
      default: '#f0f4f8',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Cairo", "Segoe UI", "Roboto", "Arial", sans-serif',
    h4: {
      fontWeight: 800,
      color: '#1e40af',
      textShadow: '0 2px 4px rgba(30, 64, 175, 0.1)',
    },
    h6: {
      fontWeight: 700,
      color: '#1e40af',
    },
    body1: {
      lineHeight: 1.7,
      fontSize: '1.1rem',
    },
  },
  shape: {
    borderRadius: 20,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
          boxShadow: '0 4px 20px rgba(30, 64, 175, 0.3)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 15,
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '1rem',
          padding: '12px 24px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 6px 20px rgba(0, 0, 0, 0.25)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
  },
});

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(Date.now().toString());
  const [messageCount, setMessageCount] = useState(0);
  const [showWelcome, setShowWelcome] = useState(true);
  const [showAbout, setShowAbout] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking', 'connected', 'error'
  const [backendInfo, setBackendInfo] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // إضافة رسالة ترحيب عند بدء التطبيق
  useEffect(() => {
    setTimeout(() => setShowWelcome(false), 3000);
    setMessages([
      {
        id: 1,
        text: "مرحباً بك في المساعد التعليمي الذكي لمؤسسة قدها! 🎓\n\nأنا هنا لمساعدتك في:\n• حل المسائل الرياضية والعلمية\n• شرح المفاهيم التعليمية\n• الإجابة على أسئلتك الدراسية\n• تقديم الدعم التعليمي المتقدم\n\nكيف يمكنني مساعدتك اليوم؟",
        sender: 'bot',
        timestamp: new Date(),
      }
    ]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setMessageCount(prev => prev + 1);

    try {
      // Send request in the exact format expected by the backend
      const response = await axios.post('http://localhost:5000/chat', {
        message: inputMessage,
        session_id: sessionId
      }, {
        timeout: 30000 // 30 second timeout for model responses
      });

      // Handle response from the backend model
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      let errorText = "عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني.";
      
      if (error.code === 'ECONNABORTED') {
        errorText = "انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى.";
      } else if (error.response?.status === 500) {
        errorText = "حدث خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً.";
      } else if (error.response?.status === 400) {
        errorText = "طلب غير صحيح. يرجى التأكد من صحة الرسالة.";
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim()) {
        handleSendMessage();
        setInputMessage(''); // Clear input immediately
      }
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        text: "تم مسح المحادثة. مرحباً بك من جديد في المساعد التعليمي الذكي لمؤسسة قدها! 🎓\n\nكيف يمكنني مساعدتك اليوم؟",
        sender: 'bot',
        timestamp: new Date(),
      }
    ]);
    setMessageCount(0);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('ar-SA', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const suggestedQuestions = [
    "كيف أحسب مساحة الدائرة؟",
    "اشرح لي نظرية فيثاغورس",
    "ما هو الجذر التربيعي للعدد 16؟",
    "كيف أحل المعادلة التربيعية؟",
    "ما هي خصائص المثلث؟",
    "كيف أحسب حجم الكرة؟"
  ];

  const handleSuggestedQuestion = (question) => {
    setInputMessage(question);
  };

  const retryConnection = async () => {
    await testBackendConnection();
  };

  // Test backend connection and model integration
  const testBackendConnection = async () => {
    try {
      setBackendStatus('checking');
      const response = await axios.get('http://localhost:5000/health', {
        timeout: 5000
      });
      console.log('Backend connection successful:', response.data);
      setBackendStatus('connected');
      setBackendInfo(response.data);
      return true;
    } catch (error) {
      console.error('Backend connection failed:', error);
      setBackendStatus('error');
      setBackendInfo({
        error: error.message,
        details: error.response?.data || 'Connection timeout or server not running'
      });
      return false;
    }
  };

  // Test the model with a sample question
  const testModel = async () => {
    try {
      const testResponse = await axios.post('http://localhost:5000/chat', {
        message: "ما هو 2 + 2؟",
        session_id: "test-session"
      }, {
        timeout: 10000
      });
      console.log('Model test successful:', testResponse.data);
      return true;
    } catch (error) {
      console.error('Model test failed:', error);
      return false;
    }
  };

  // Test connection on component mount
  useEffect(() => {
    testBackendConnection();
    // Uncomment the line below to test the model on startup
    // testModel();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <AppBar position="static" elevation={0}>
          <Toolbar sx={{ py: 1 }}>
            <SchoolIcon sx={{ mr: 2, fontSize: 36, filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h5" component="div" sx={{ fontWeight: 800, mb: 0.5 }}>
                مؤسسة قدها التعليمية
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, fontSize: '0.9rem' }}>
                المساعد التعليمي الذكي
              </Typography>
            </Box>
            <Badge badgeContent={messageCount} color="secondary" sx={{ mr: 2 }}>
              <BotIcon sx={{ fontSize: 28 }} />
            </Badge>
            
            {/* Connection Status Indicator */}
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              mr: 2,
              borderRadius: 1,
              px: 1,
              py: 0.5,
              backgroundColor: backendStatus === 'connected' ? 'rgba(34, 197, 94, 0.1)' : 
                              backendStatus === 'error' ? 'rgba(239, 68, 68, 0.1)' : 
                              'rgba(245, 158, 11, 0.1)',
              border: `1px solid ${
                backendStatus === 'connected' ? 'rgba(34, 197, 94, 0.3)' : 
                backendStatus === 'error' ? 'rgba(239, 68, 68, 0.3)' : 
                'rgba(245, 158, 11, 0.3)'
              }`
            }}>
              <Box sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: backendStatus === 'connected' ? '#22c55e' : 
                                backendStatus === 'error' ? '#ef4444' : '#f59e0b',
                mr: 0.5,
                animation: backendStatus === 'checking' ? 'pulse 1.5s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 }
                }
              }} />
              <Typography variant="caption" sx={{ 
                fontSize: '0.7rem',
                fontWeight: 600,
                color: backendStatus === 'connected' ? '#22c55e' : 
                       backendStatus === 'error' ? '#ef4444' : '#f59e0b'
              }}>
                {backendStatus === 'connected' ? 'متصل' : 
                 backendStatus === 'error' ? 'غير متصل' : 'جاري الاتصال...'}
              </Typography>
            </Box>
            <IconButton 
              color="inherit" 
              onClick={clearChat} 
              title="مسح المحادثة"
              sx={{ 
                '&:hover': { 
                  transform: 'rotate(180deg)',
                  transition: 'transform 0.5s ease'
                }
              }}
            >
              <RefreshIcon />
            </IconButton>
          </Toolbar>
        </AppBar>

        {/* Welcome Animation */}
        {showWelcome && (
          <Fade in={showWelcome} timeout={1000}>
            <Box
              sx={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                bgcolor: 'rgba(30, 64, 175, 0.95)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 9999,
                color: 'white',
              }}
            >
              <Zoom in={showWelcome} timeout={1500}>
                <SchoolIcon sx={{ fontSize: 120, mb: 3, filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))' }} />
              </Zoom>
              <Slide direction="up" in={showWelcome} timeout={2000}>
                <Typography variant="h3" sx={{ fontWeight: 800, textAlign: 'center', mb: 2 }}>
                  مؤسسة قدها التعليمية
                </Typography>
              </Slide>
              <Slide direction="up" in={showWelcome} timeout={2500}>
                <Typography variant="h5" sx={{ opacity: 0.9, textAlign: 'center' }}>
                  المساعد التعليمي الذكي
                </Typography>
              </Slide>
            </Box>
          </Fade>
        )}

        {/* Main Content */}
        <Container maxWidth={false} sx={{ flexGrow: 1, py: 0, px: 0, height: 'calc(100vh - 64px)' }}>
          <Grid container spacing={0} sx={{ height: 'calc(100vh - 64px)' }}>
            {/* Chat Area */}
            <Grid item xs={12} sx={{ height: 'calc(100vh - 64px)' }}>
              <Box 
                sx={{ 
                  height: 'calc(100vh - 64px)', 
                  display: 'flex', 
                  flexDirection: 'column',
                  overflow: 'hidden',
                  background: '#f8fafc',
                  position: 'relative'
                }}
              >
                {/* About Button - Floating */}
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setShowAbout(!showAbout)}
                  title={showAbout ? "إغلاق النبذة" : "عرض النبذة"}
                  sx={{
                    position: 'absolute',
                    top: { xs: 6, sm: 8, md: 10 },
                    left: { xs: 6, sm: 8, md: 10 },
                    zIndex: 10,
                    borderRadius: 2,
                    background: showAbout ? 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)' : 'white',
                    color: showAbout ? 'white' : '#1e40af',
                    minWidth: 'auto',
                    width: { xs: 36, sm: 40, md: 44 },
                    height: { xs: 36, sm: 40, md: 44 },
                    p: 0,
                    border: showAbout ? 'none' : '2px solid #1e40af',
                    fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                    fontWeight: 600,
                    boxShadow: showAbout ? '0 4px 15px rgba(30, 64, 175, 0.3)' : '0 2px 8px rgba(30, 64, 175, 0.15)',
                    '&:hover': {
                      background: showAbout ? 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)' : 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                      color: 'white',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 20px rgba(30, 64, 175, 0.25)',
                      border: 'none'
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  <InfoIcon sx={{ fontSize: { xs: 18, sm: 20, md: 22 } }} />
                </Button>

                {/* About Summary - Next to Button */}
                {showAbout && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: { xs: 6, sm: 8, md: 10 },
                      left: { xs: 50, sm: 56, md: 62 },
                      zIndex: 9,
                      backgroundColor: 'white',
                      borderRadius: 3,
                      border: '1px solid #e2e8f0',
                      boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                      p: { xs: 2, sm: 2.5, md: 3 },
                      maxWidth: { xs: '280px', sm: '320px', md: '360px' },
                      minWidth: { xs: '260px', sm: '300px', md: '340px' },
                      maxHeight: 'calc(100vh - 120px)',
                      overflow: 'auto'
                    }}
                  >
                    {/* Header Section */}
                    <Box sx={{ 
                      textAlign: 'center', 
                      mb: { xs: 1.5, sm: 2, md: 2.5 },
                      p: { xs: 1.5, sm: 2, md: 2.5 },
                      background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)',
                      borderRadius: 2,
                      border: '1px solid rgba(30, 64, 175, 0.1)'
                    }}>
                      <Avatar sx={{ 
                        width: { xs: 40, sm: 44, md: 48 }, 
                        height: { xs: 40, sm: 44, md: 48 }, 
                        mx: 'auto', 
                        mb: 1,
                        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                        boxShadow: '0 4px 15px rgba(30, 64, 175, 0.3)',
                        border: '3px solid white'
                      }}>
                        <SchoolIcon sx={{ fontSize: { xs: 20, sm: 22, md: 24 } }} />
                      </Avatar>
                      
                      <Typography variant="h6" gutterBottom sx={{ 
                        fontWeight: 800,
                        color: 'primary.main',
                        fontSize: { xs: '1rem', sm: '1.1rem', md: '1.2rem' },
                        mb: 0.5
                      }}>
                        مؤسسة قدها التعليمية
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ 
                        lineHeight: 1.5,
                        fontSize: { xs: '0.7rem', sm: '0.75rem', md: '0.8rem' },
                        fontWeight: 500
                      }}>
                        المساعد التعليمي الذكي المطور خصيصاً لمؤسسة قدها التعليمية
                      </Typography>
                    </Box>
                    
                    <Divider sx={{ mb: { xs: 1.5, sm: 2, md: 2.5 }, borderColor: 'rgba(30, 64, 175, 0.2)' }} />
                    
                    {/* Features Section */}
                    <Box sx={{ mb: { xs: 1.5, sm: 2, md: 2.5 } }}>
                      <Typography variant="body1" gutterBottom sx={{ 
                        mb: { xs: 1, sm: 1.5, md: 2 },
                        fontWeight: 700,
                        color: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        fontSize: { xs: '0.8rem', sm: '0.85rem', md: '0.9rem' }
                      }}>
                        <TrendingIcon sx={{ mr: 0.5, color: 'secondary.main', fontSize: 18 }} />
                        يمكنني مساعدتك في:
                      </Typography>
                      
                      <Grid container spacing={0.5}>
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)',
                            border: '1px solid rgba(30, 64, 175, 0.1)',
                            textAlign: 'center',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              transform: 'translateY(-1px)',
                              boxShadow: '0 2px 8px rgba(30, 64, 175, 0.15)',
                            }
                          }}>
                            <CalculateIcon sx={{ 
                              fontSize: { xs: 18, sm: 20, md: 22 }, 
                              color: 'primary.main',
                              mb: 0.5
                            }} />
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: 'primary.main'
                            }}>
                              حل المسائل الرياضية
                            </Typography>
                          </Box>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(5, 150, 105, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)',
                            border: '1px solid rgba(5, 150, 105, 0.1)',
                            textAlign: 'center',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              transform: 'translateY(-1px)',
                              boxShadow: '0 2px 8px rgba(5, 150, 105, 0.15)',
                            }
                          }}>
                            <ScienceIcon sx={{ 
                              fontSize: { xs: 18, sm: 20, md: 22 }, 
                              color: 'secondary.main',
                              mb: 0.5
                            }} />
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: 'secondary.main'
                            }}>
                              شرح المفاهيم العلمية
                            </Typography>
                          </Box>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(251, 191, 36, 0.05) 100%)',
                            border: '1px solid rgba(245, 158, 11, 0.1)',
                            textAlign: 'center',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              transform: 'translateY(-1px)',
                              boxShadow: '0 2px 8px rgba(245, 158, 11, 0.15)',
                            }
                          }}>
                            <BookIcon sx={{ 
                              fontSize: { xs: 18, sm: 20, md: 22 }, 
                              color: '#f59e0b',
                              mb: 0.5
                            }} />
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: '#f59e0b'
                            }}>
                              الإجابة على الأسئلة التعليمية
                            </Typography>
                          </Box>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(196, 181, 253, 0.05) 100%)',
                            border: '1px solid rgba(168, 85, 247, 0.1)',
                            textAlign: 'center',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              transform: 'translateY(-1px)',
                              boxShadow: '0 2px 8px rgba(168, 85, 247, 0.15)',
                            }
                          }}>
                            <LightbulbIcon sx={{ 
                              fontSize: { xs: 18, sm: 20, md: 22 }, 
                              color: '#a855f7',
                              mb: 0.5
                            }} />
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: '#a855f7'
                            }}>
                              تقديم الدعم التعليمي
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>

                    <Divider sx={{ my: { xs: 1.5, sm: 2, md: 2.5 }, borderColor: 'rgba(30, 64, 175, 0.2)' }} />

                    {/* Suggested Questions Section */}
                    <Box sx={{ mb: { xs: 1.5, sm: 2, md: 2.5 } }}>
                      <Typography variant="body1" gutterBottom sx={{ 
                        mb: { xs: 1, sm: 1.5, md: 2 },
                        fontWeight: 700,
                        color: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        fontSize: { xs: '0.8rem', sm: '0.85rem', md: '0.9rem' }
                      }}>
                        <EmojiIcon sx={{ mr: 0.5, color: 'secondary.main', fontSize: 18 }} />
                        أسئلة مقترحة:
                      </Typography>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {suggestedQuestions.map((question, index) => (
                          <Button
                            key={index}
                            variant="outlined"
                            size="small"
                            onClick={() => handleSuggestedQuestion(question)}
                            startIcon={<ChatIcon sx={{ fontSize: 14 }} />}
                            sx={{ 
                              justifyContent: 'flex-start',
                              textAlign: 'right',
                              borderRadius: 1.5,
                              textTransform: 'none',
                              fontSize: { xs: '0.65rem', sm: '0.7rem', md: '0.75rem' },
                              fontWeight: 500,
                              borderColor: 'rgba(30, 64, 175, 0.3)',
                              color: 'primary.main',
                              backgroundColor: 'rgba(30, 64, 175, 0.02)',
                              '&:hover': {
                                borderColor: 'primary.main',
                                backgroundColor: 'rgba(30, 64, 175, 0.08)',
                                transform: 'translateX(-2px)',
                                boxShadow: '0 2px 8px rgba(30, 64, 175, 0.15)',
                              },
                              transition: 'all 0.2s ease',
                              p: { xs: 1, sm: 1.2, md: 1.5 }
                            }}
                          >
                            {question}
                          </Button>
                        ))}
                      </Box>
                    </Box>

                    <Divider sx={{ my: { xs: 1.5, sm: 2, md: 2.5 }, borderColor: 'rgba(30, 64, 175, 0.2)' }} />

                    {/* Stats Section */}
                    <Box sx={{ mb: { xs: 1.5, sm: 2, md: 2.5 } }}>
                      <Typography variant="body1" gutterBottom sx={{ 
                        mb: { xs: 1, sm: 1.5, md: 2 },
                        fontWeight: 700,
                        color: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        fontSize: { xs: '0.8rem', sm: '0.85rem', md: '0.9rem' }
                      }}>
                        <BarChartIcon sx={{ mr: 0.5, color: 'secondary.main', fontSize: 18 }} />
                        إحصائيات النظام:
                      </Typography>
                      
                      <Grid container spacing={0.5}>
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)',
                            border: '1px solid rgba(34, 197, 94, 0.2)',
                            textAlign: 'center'
                          }}>
                            <Typography variant="h6" sx={{ 
                              fontWeight: 900,
                              color: '#22c55e',
                              fontSize: { xs: '1.2rem', sm: '1.3rem', md: '1.4rem' }
                            }}>
                              24/7
                            </Typography>
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: '#22c55e'
                            }}>
                              متاح دائماً
                            </Typography>
                          </Box>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Box sx={{ 
                            p: { xs: 1, sm: 1.2, md: 1.5 },
                            borderRadius: 2,
                            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(30, 64, 175, 0.1) 100%)',
                            border: '1px solid rgba(59, 130, 246, 0.2)',
                            textAlign: 'center'
                          }}>
                            <Typography variant="h6" sx={{ 
                              fontWeight: 900,
                              color: '#3b82f6',
                              fontSize: { xs: '1.2rem', sm: '1.3rem', md: '1.4rem' }
                            }}>
                              100%
                            </Typography>
                            <Typography variant="caption" sx={{ 
                              display: 'block',
                              fontWeight: 600,
                              fontSize: { xs: '0.6rem', sm: '0.65rem', md: '0.7rem' },
                              color: '#3b82f6'
                            }}>
                              دقة في الإجابات
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>

                    <Divider sx={{ my: { xs: 1.5, sm: 2, md: 2.5 }, borderColor: 'rgba(30, 64, 175, 0.2)' }} />

                    {/* Tips Section */}
                    <Box sx={{ 
                      backgroundColor: 'rgba(30, 64, 175, 0.05)',
                      p: { xs: 1.5, sm: 2, md: 2.5 },
                      borderRadius: 2,
                      border: '1px solid rgba(30, 64, 175, 0.1)',
                      textAlign: 'center'
                    }}>
                      <Typography variant="body1" gutterBottom sx={{ 
                        fontWeight: 700,
                        color: 'primary.main',
                        fontSize: { xs: '0.8rem', sm: '0.85rem', md: '0.9rem' },
                        mb: { xs: 1, sm: 1.5, md: 2 }
                      }}>
                        💡 نصائح للاستخدام الأمثل
                      </Typography>
                      
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, textAlign: 'right' }}>
                        <Typography variant="body2" sx={{ 
                          fontSize: { xs: '0.65rem', sm: '0.7rem', md: '0.75rem' },
                          color: 'text.secondary',
                          fontWeight: 500,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}>
                          <CheckCircleIcon sx={{ fontSize: 14, color: '#22c55e' }} />
                          Enter لإرسال الرسالة
                        </Typography>
                        
                        <Typography variant="body2" sx={{ 
                          fontSize: { xs: '0.65rem', sm: '0.7rem', md: '0.75rem' },
                          color: 'text.secondary',
                          fontWeight: 500,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}>
                          <CheckCircleIcon sx={{ fontSize: 14, color: '#22c55e' }} />
                          Shift+Enter للسطر الجديد
                        </Typography>
                        
                        <Typography variant="body2" sx={{ 
                          fontSize: { xs: '0.65rem', sm: '0.7rem', md: '0.75rem' },
                          color: 'text.secondary',
                          fontWeight: 500,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}>
                          <CheckCircleIcon sx={{ fontSize: 14, color: '#22c55e' }} />
                          يمكنك كتابة أسئلة طويلة أو قصيرة
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                )}

                {/* Messages Area - Scrollable */}
                <Box sx={{ 
                  flexGrow: 1, 
                  overflow: 'auto', 
                  p: { xs: 1, sm: 1.5, md: 2 },
                  background: '#f8fafc',
                  pt: { xs: 3, sm: 4, md: 5 }
                }}>
                  {messages.map((message, index) => (
                    <Fade in={true} timeout={500 + index * 100} key={message.id}>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                          mb: { xs: 1, sm: 1.5, md: 2 },
                        }}
                      >
                        <Box
                          sx={{
                            maxWidth: { xs: '88%', sm: '82%', md: '75%' },
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: { xs: 0.8, sm: 1, md: 1.5 },
                          }}
                        >
                          {message.sender === 'bot' && (
                            <Avatar sx={{ 
                              bgcolor: 'primary.main', 
                              width: { xs: 24, sm: 28, md: 32 }, 
                              height: { xs: 24, sm: 28, md: 32 },
                              boxShadow: '0 2px 6px rgba(30, 64, 175, 0.15)',
                              border: '2px solid white',
                              display: { xs: 'none', sm: 'flex' }
                            }}>
                              <BotIcon />
                            </Avatar>
                          )}
                          <Box>
                            <Box
                              sx={{
                                p: { xs: 1, sm: 1.5, md: 2 },
                                backgroundColor: message.sender === 'user' 
                                  ? '#e2e8f0' 
                                  : 'white',
                                color: 'text.primary',
                                borderRadius: 1.5,
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.06)',
                                position: 'relative',
                                maxWidth: '100%'
                              }}
                            >
                              <Typography variant="body1" sx={{ 
                                lineHeight: 1.4, 
                                fontSize: { xs: '0.7rem', sm: '0.75rem', md: '0.8rem' },
                                textAlign: { xs: 'center', sm: 'left' },
                                fontWeight: 500
                              }}>
                                {formatMessageText(message.text)}
                              </Typography>
                            </Box>
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                mt: { xs: 0.3, sm: 0.5, md: 0.8 }, 
                                display: 'block',
                                color: 'text.secondary',
                                textAlign: message.sender === 'user' ? 'right' : 'left',
                                fontSize: { xs: '0.55rem', sm: '0.6rem', md: '0.65rem' },
                                fontWeight: 600,
                                opacity: 0.6
                              }}
                            >
                              {formatTime(message.timestamp)}
                            </Typography>
                          </Box>
                          {message.sender === 'user' && (
                            <Avatar sx={{ 
                              bgcolor: 'secondary.main', 
                              width: { xs: 24, sm: 28, md: 32 }, 
                              height: { xs: 24, sm: 28, md: 32 },
                              boxShadow: '0 2px 6px rgba(5, 150, 105, 0.15)',
                              border: '2px solid white',
                              display: { xs: 'none', sm: 'flex' }
                            }}>
                              <PersonIcon />
                            </Avatar>
                          )}
                        </Box>
                      </Box>
                    </Fade>
                  ))}
                  {isLoading && (
                    <Fade in={isLoading} timeout={500}>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: { xs: 1, sm: 1.5, md: 2 } }}>
                        <Avatar sx={{ 
                          bgcolor: 'primary.main', 
                          width: { xs: 24, sm: 28, md: 32 }, 
                          height: { xs: 24, sm: 28, md: 32 }, 
                          mr: { xs: 0.8, sm: 1, md: 1.5 },
                          boxShadow: '0 2px 6px rgba(30, 64, 175, 0.15)',
                          border: '2px solid white',
                          display: { xs: 'none', sm: 'flex' }
                        }}>
                          <BotIcon />
                        </Avatar>
                        <Box sx={{ 
                          p: { xs: 1, sm: 1.5, md: 2 }, 
                          borderRadius: 1.5, 
                          background: 'white',
                          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.06)'
                        }}>
                          <CircularProgress size={{ xs: 16, sm: 18, md: 20 }} />
                        </Box>
                      </Box>
                    </Fade>
                  )}
                  <div ref={messagesEndRef} />
                </Box>

                {/* Input Area - Fixed at Bottom */}
                <Box sx={{ 
                  p: { xs: 0.8, sm: 1, md: 1.5 }, 
                  borderTop: '1px solid #e2e8f0',
                  backgroundColor: 'white',
                  flexShrink: 0
                }}>
                  <Box sx={{ 
                    display: 'flex', 
                    gap: { xs: 0.5, sm: 0.8 }, 
                    alignItems: 'flex-end',
                    flexDirection: 'row'
                  }}>
                    <TextField
                      fullWidth
                      multiline
                      minRows={1}
                      maxRows={2}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="اكتب سؤالك هنا..."
                      variant="outlined"
                      size="small"
                      disabled={isLoading}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                          backgroundColor: '#f8fafc',
                          fontSize: { xs: '0.6rem', sm: '0.7rem', md: '0.75rem' },
                          minHeight: { xs: '32px', sm: '32px', md: '36px' },
                          border: '1px solid #e2e8f0',
                          '&:hover': {
                            backgroundColor: '#f1f5f9',
                            borderColor: '#cbd5e1',
                          },
                          '&.Mui-focused': {
                            backgroundColor: 'white',
                            borderColor: '#1e40af',
                            boxShadow: '0 0 0 2px rgba(30, 64, 175, 0.1)',
                          },
                          '& .MuiOutlinedInput-input': {
                            padding: { xs: '6px 10px', sm: '6px 10px', md: '8px 12px' },
                            lineHeight: 1.3,
                            fontWeight: 500
                          }
                        },
                        '& .MuiInputLabel-root': {
                          fontSize: { xs: '0.3rem', sm: '0.4rem', md: '0.45rem' },
                          color: '#64748b',
                          fontWeight: 500
                        }
                      }}
                    />
                    
                    {/* زر تحميل الصورة - محسن */}
                    <Button
                      variant="outlined"
                      size="small"
                      disabled={true}
                      title="تحميل الصورة (سيتم تفعيله قريباً)"
                      sx={{ 
                        borderRadius: 2,
                        minWidth: { xs: 40, sm: 36 },
                        height: { xs: 32, sm: 32 },
                        borderColor: '#d1d5db',
                        color: '#6b7280',
                        backgroundColor: '#f9fafb',
                        borderWidth: '1px',
                        '&:hover': {
                          borderColor: '#9ca3af',
                          backgroundColor: '#f3f4f6',
                          transform: 'translateY(-1px)',
                          boxShadow: '0 1px 4px rgba(156, 163, 175, 0.12)',
                        },
                        '&:disabled': {
                          borderColor: '#d1d5db',
                          color: '#9ca3af',
                          backgroundColor: '#f9fafb',
                        },
                        transition: 'all 0.1s ease',
                      }}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                      </svg>
                    </Button>
                    
                    {/* زر الإرسال - محسن */}
                    <Button
                      variant="contained"
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                      sx={{ 
                        borderRadius: 2,
                        minWidth: { xs: 40, sm: 36 },
                        height: { xs: 32, sm: 32 },
                        background: '#1e40af',
                        '&:hover': {
                          background: '#1e3a8a',
                          transform: 'translateY(-1px)',
                          boxShadow: '0 2px 6px rgba(30, 64, 175, 0.2)',
                        },
                        '&:disabled': {
                          background: '#cbd5e1',
                          transform: 'none',
                          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.08)',
                        },
                        transition: 'all 0.1s ease',
                      }}
                    >
                      <SendIcon sx={{ fontSize: 14 }} />
                    </Button>
                  </Box>
                  
                  {/* نص مساعد - محسن */}
                  <Typography variant="caption" color="text.secondary" sx={{ 
                    mt: { xs: 0.3, sm: 0.5, md: 0.8 }, 
                    display: 'block',
                    textAlign: 'center',
                    fontSize: { xs: '0.5rem', sm: '0.55rem', md: '0.6rem' },
                    opacity: 0.9,
                    fontWeight: 400,
                    color: '#64748b'
                  }}>
                    💡 Enter للإرسال • Shift+Enter للسطر الجديد
                  </Typography>
                  
                  {/* Footer */}
                  <Box sx={{ 
                    mt: { xs: 0.5, sm: 1, md: 1.5 },
                    pt: { xs: 0.5, sm: 1, md: 1.5 },
                    borderTop: '1px solid #e2e8f0',
                    textAlign: 'center'
                  }}>
                    <Typography variant="caption" sx={{ 
                      fontSize: { xs: '0.45rem', sm: '0.5rem', md: '0.55rem' },
                      color: '#9ca3af',
                      fontWeight: 500,
                      opacity: 0.9
                    }}>
                      © 2025 مؤسسة قدها التعليمية. جميع الحقوق محفوظة
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
