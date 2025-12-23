import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, IconButton, Fab, TextField, Typography, Card, CardContent, CardMedia, Slide, Chip, Fade, Paper, Badge } from '@mui/material';
import { Mic, Send, Keyboard, Close, MoreVert, CallEnd, ShoppingCart } from '@mui/icons-material';
import OrbVisualizer from './components/OrbVisualizer';
import { useAssistant } from './hooks/useAssistant';

// Dark Theme Configuration
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#000000',
    },
    primary: {
      main: '#d0bcff',
    },
    secondary: {
      main: '#ccc2dc',
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
  shape: {
    borderRadius: 12,
  }
});

function App() {
  const {
    status, isListening, isSpeaking, isThinking, analyser, products,
    liveUserText, liveAiText,
    startListening, stopListening, sendMessage
  } = useAssistant();

  const [showInput, setShowInput] = useState(false);
  const [inputText, setInputText] = useState('');

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
    <ThemeProvider theme={darkTheme}>
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
        <Paper elevation={24} sx={{
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
            <Typography variant="h6" sx={{ color: 'text.secondary', fontWeight: 500 }}>AI Assistant</Typography>
            <IconButton><MoreVert /></IconButton>
          </Box>

          {/* Visualizer Area */}
          <Box sx={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <OrbVisualizer
              isListening={isListening}
              isSpeaking={isSpeaking}
              isThinking={isThinking}
              analyser={analyser}
            />

            {/* Live Transcript Overlay */}
            <Box sx={{
              position: 'absolute',
              top: '15%',
              left: 0,
              right: 0,
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              pointerEvents: 'none',
              zIndex: 5
            }}>
              {/* AI Transcript */}
              <Fade in={!!liveAiText}>
                <Typography
                  variant="h5"
                  align="center"
                  sx={{
                    color: 'primary.light',
                    textShadow: '0 0 10px rgba(208,188,255,0.5)',
                    fontWeight: 400,
                    px: 2
                  }}
                >
                  {liveAiText}
                </Typography>
              </Fade>

              {/* User Transcript */}
              <Fade in={!!liveUserText}>
                <Typography
                  variant="h5"
                  align="center"
                  sx={{
                    color: 'text.primary',
                    opacity: 0.9,
                    fontStyle: 'italic',
                    px: 2
                  }}
                >
                  "{liveUserText}"
                </Typography>
              </Fade>
            </Box>

            {/* Status Chip */}
            <Chip
              label={status}
              sx={{
                position: 'absolute',
                bottom: '15%',
                opacity: isListening || isThinking || isSpeaking ? 1 : 0.6,
                transition: 'opacity 0.3s',
                bgcolor: 'rgba(0,0,0,0.5)'
              }}
            />
          </Box>

          {/* Products Overlay */}
          <Fade in={products.length > 0}>
            <Box sx={{
              position: 'absolute',
              top: 70,
              left: 0,
              right: 0,
              bottom: 120,
              p: 2,
              overflowY: 'auto',
              background: 'linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.95) 15%)',
              pointerEvents: products.length > 0 ? 'auto' : 'none',
              zIndex: 6
            }}>
              {products.map((p, i) => (
                <Card key={i} sx={{ mb: 2, display: 'flex', alignItems: 'center', p: 1, bgcolor: 'rgba(30,30,30,0.95)' }}>
                  <CardMedia
                    component="img"
                    sx={{ width: 80, height: 80, borderRadius: 2 }}
                    image={p.metadata.image_url}
                    alt={p.metadata.title}
                  />
                  <CardContent sx={{ flex: 1, py: 0 }}>
                    <Typography variant="subtitle2" noWrap>{p.metadata.title}</Typography>
                    <Typography variant="body2" color="primary">₹{p.metadata.price}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </Fade>

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
      </Box>
    </ThemeProvider>
  );
}

export default App;
