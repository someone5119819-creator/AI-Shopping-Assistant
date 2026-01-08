import React, { useState, useRef, useEffect } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, IconButton, Fab, TextField, Typography, Card, CardContent, CardMedia, Slide, Chip, Fade, Paper, Badge } from '@mui/material';
import { Mic, Send, Keyboard, Close, MoreVert, CallEnd, ShoppingCart, CameraAlt, FiberManualRecord } from '@mui/icons-material';
import OrbVisualizer from './components/OrbVisualizer';
import { useAssistant } from './hooks/useAssistant';
import CartModal from './components/CartModal';

// Light Theme Configuration
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    background: {
      default: '#f2f2f2',
      paper: '#ffffff',
    },
    primary: {
      main: '#0026ffff', // A nice vibrant purple/blue
    },
    secondary: {
      main: '#03dac6',
    },
    text: {
      primary: '#1c1b1f',
      secondary: '#616161',
    }
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
  },
  shape: {
    borderRadius: 16,
  }
});

function App() {
  const {
    status, isListening, isSpeaking, isThinking, analyser, products,
    liveUserText, liveAiText, isCameraOpen, setIsCameraOpen, analyzeImage,
    cartItems, cartCount, addToCart, viewCart, clearCart,
    startListening, stopListening, sendMessage
  } = useAssistant();

  const [showInput, setShowInput] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isCartOpen, setIsCartOpen] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    let stream = null;
    let timer = null;

    if (isCameraOpen) {
      // Start Video Stream
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(s => {
          stream = s;
          if (videoRef.current) videoRef.current.srcObject = s;

          // Auto-Capture Timer
          timer = setTimeout(() => {
            handleCapture();
          }, 2000); // 2 seconds
        })
        .catch(err => {
          console.error("Camera Error:", err);
          setIsCameraOpen(false);
        });
    }

    return () => {
      if (stream) stream.getTracks().forEach(track => track.stop());
      if (timer) clearTimeout(timer);
    };
  }, [isCameraOpen]);

  const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      canvas.toBlob(blob => {
        analyzeImage(blob);
      }, 'image/jpeg', 0.8);
    }
  };

  const toggleMic = () => {
    if (isListening) stopListening();
    else startListening();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      sendMessage(inputText);
      setInputText('');
      setShowInput(false);
    }
  };

  const endSession = () => {
    if (window.confirm("End Session?")) window.location.reload();
  };

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />

      {/* Outer Container - Centers the Widget */}
      <Box sx={{
        height: '100vh',
        width: '100vw',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        bgcolor: 'background.default',
        overflow: 'hidden'
      }}>

        {/* Widget Container - Max 600px */}
        <Paper elevation={0} sx={{
          width: '100%',
          maxWidth: '500px',
          height: '100%',
          maxHeight: { xs: '100%', md: '900px' },
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper',
          overflow: 'hidden',
          position: 'relative',
          borderRadius: { xs: 0, md: 2 }
        }}>

          {/* Header */}
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 10 }}>
            <IconButton onClick={() => window.close()}><Close /></IconButton>
            <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 500 }}>AI Assistant</Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <IconButton onClick={async () => { await viewCart(); setIsCartOpen(true); }}>
                <Badge badgeContent={cartCount} color="primary">
                  <ShoppingCart />
                </Badge>
              </IconButton>
              <Chip
                label={status}
                size="small"
                sx={{
                  bgcolor: isListening || isThinking || isSpeaking ? 'rgba(98, 0, 238, 0.08)' : '#f5f5f5',
                  color: isListening || isThinking || isSpeaking ? 'primary.main' : 'text.secondary',
                  fontWeight: 600,
                  border: 'none'
                }}
              />
            </Box>
          </Box>

          {/* Visualizer Area */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', pt: 3, gap: 2 }}>

            {/* Orb Rectangle (Mask) */}
            <Box sx={{
              width: '90%',
              height: '104px',
              bgcolor: '#f9f9f9',
              borderRadius: 3,
              border: '1px solid rgba(0,0,0,0.05)',
              position: 'relative',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Large Orb Container (Absolute & Centered) */}
              <Box sx={{
                position: 'absolute',
                width: '100%',
                height: '300px',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <OrbVisualizer
                  isListening={isListening}
                  isSpeaking={isSpeaking}
                  isThinking={isThinking}
                  analyser={analyser}
                />
              </Box>


            </Box>

            {/* Dynamic Content Area (Transcript or Products) */}
            <Box sx={{
              width: '90%',
              flex: 1, // Fill remaining space
              minHeight: '200px', // Min height
              bgcolor: '#f7f7f7ff',
              borderRadius: 3,
              border: '1px solid rgba(0,0,0,0.05)',
              p: 2,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative'
            }}>

              {/* Camera View */}
              <Fade in={isCameraOpen} unmountOnExit>
                <Box sx={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  bgcolor: 'black', zIndex: 10,
                  display: 'flex', flexDirection: 'column',
                  overflow: 'hidden', borderRadius: 4,
                  alignItems: 'center', justifyContent: 'center'
                }}>
                  <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.6 }} />
                  <canvas ref={canvasRef} style={{ display: 'none' }} />

                  {/* Scanning Overlay */}
                  <Box sx={{
                    position: 'absolute',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2
                  }}>
                    <div className="scanner-animation" style={{
                      width: '200px', height: '2px', background: 'cyan',
                      boxShadow: '0 0 10px cyan',
                      animation: 'scan 1.5s infinite ease-in-out'
                    }} />
                    <Typography variant="h6" sx={{ color: 'cyan', fontWeight: 'bold', letterSpacing: 2 }}>
                      SCANNING...
                    </Typography>
                  </Box>

                  <IconButton onClick={() => setIsCameraOpen(false)} sx={{ position: 'absolute', top: 10, right: 10, color: 'white' }}>
                    <Close />
                  </IconButton>
                </Box>
              </Fade>

              {/* Product Recommendations View */}
              <Fade in={products.length > 0} unmountOnExit>
                <Box sx={{
                  position: 'absolute',
                  top: 0, left: 0, right: 0, bottom: 0,
                  overflowY: 'auto',
                  p: 2,
                  zIndex: 2,
                  '&::-webkit-scrollbar': { display: 'none' },
                  msOverflowStyle: 'none',
                  scrollbarWidth: 'none',
                }}>

                  {products.map((p, i) => (
                    <Card key={i} elevation={0} sx={{
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center',
                      p: 2,
                      bgcolor: '#ffffff',
                      border: '1px solid rgba(0,0,0,0.05)',
                      borderRadius: 2
                    }}>
                      <CardMedia
                        component="img"
                        sx={{ width: 70, height: 70, borderRadius: 2 }}
                        image={p.metadata.image_url}
                        alt={p.metadata.title}
                      />
                      <CardContent sx={{ flex: 1, py: 0, px: 2, '&:last-child': { pb: 0 } }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, lineHeight: 1.2, mb: 0.5 }}>
                          {p.metadata.title}
                        </Typography>
                        <Typography variant="body2" color="primary" fontWeight="bold">
                          ₹{p.metadata.price}
                        </Typography>
                      </CardContent>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => addToCart({
                          id: p.metadata.product_id,
                          title: p.metadata.title,
                          image: p.metadata.image_url
                        })}
                      >
                        <ShoppingCart fontSize="small" />
                      </IconButton>
                    </Card>
                  ))}
                </Box>
              </Fade>

              {/* Live Transcript View (Default) */}
              <Fade in={products.length === 0}>
                <Box sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2
                }}>
                  {/* AI Transcript */}
                  <Fade in={!!liveAiText}>
                    <Typography
                      variant="h6"
                      align="center"
                      sx={{
                        color: 'primary.main',
                        fontWeight: 500,
                        px: 1,
                        display: '-webkit-box',
                        overflow: 'hidden',
                        WebkitBoxOrient: 'vertical',
                        WebkitLineClamp: 4, // Allow slightly more lines in this larger box
                      }}
                    >
                      {liveAiText}
                    </Typography>
                  </Fade>

                  {/* User Transcript */}
                  <Fade in={!!liveUserText}>
                    <Typography
                      variant="subtitle1"
                      align="center"
                      sx={{
                        color: 'text.secondary',
                        fontStyle: 'italic',
                        px: 1,
                        display: '-webkit-box',
                        overflow: 'hidden',
                        WebkitBoxOrient: 'vertical',
                        WebkitLineClamp: 2,
                      }}
                    >
                      "{liveUserText}"
                    </Typography>
                  </Fade>
                </Box>
              </Fade>

            </Box>
          </Box>

          {/* Bottom Controls */}
          <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', gap: 4, alignItems: 'center', zIndex: 10 }}>
            <IconButton onClick={() => setShowInput(!showInput)} sx={{ bgcolor: 'rgba(255,255,255,0.05)', width: 56, height: 56 }}>
              <Keyboard />
            </IconButton>

            <Fab
              color={isListening ? "default" : "primary"}
              onClick={toggleMic}
              sx={{
                width: 72,
                height: 72,
                '& .MuiSvgIcon-root': { fontSize: 32 },
                boxShadow: isListening ? '0 0 24px rgba(208,188,255,0.6)' : 'none',
                transition: 'all 0.3s'
              }}
            >
              <Mic />
            </Fab>

            <IconButton onClick={endSession} sx={{ bgcolor: 'rgba(244, 67, 54, 0.2)', color: '#f44336', width: 56, height: 56 }}>
              <CallEnd />
            </IconButton>
          </Box>

          {/* Text Input Sheet */}
          <Slide direction="up" in={showInput} mountOnEnter unmountOnExit>
            <Box component="form" onSubmit={handleSubmit} sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              p: 3,
              bgcolor: 'background.paper',
              borderRadius: '24px 24px 0 0',
              zIndex: 20,
              boxShadow: 24
            }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Message assistant..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  autoFocus
                  variant="outlined"
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 4 } }}
                />
                <IconButton type="submit" color="primary"><Send /></IconButton>
              </Box>
            </Box>
          </Slide>

        </Paper>

        {/* Simple Cart Modal */}
        <CartModal
          open={isCartOpen}
          onClose={() => setIsCartOpen(false)}
          cartItems={cartItems}
          cartCount={cartCount}
          onClear={async () => {
            await clearCart();
            setIsCartOpen(false);
          }}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
