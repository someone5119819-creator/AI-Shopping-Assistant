import React, { useRef, useEffect } from 'react';
import { Box } from '@mui/material';

const OrbVisualizer = ({ isListening, isSpeaking, isThinking, analyser }) => {
    const canvasRef = useRef(null);
    const animationRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;

        // Resize handler
        const resize = () => {
            const parent = canvas.parentElement;
            if (parent) {
                canvas.width = parent.clientWidth * dpr;
                canvas.height = parent.clientHeight * dpr;
                ctx.scale(dpr, dpr);
            }
        };
        resize();
        window.addEventListener('resize', resize);

        // Orb State
        let orb = {
            radius: 50,
            color: '100, 100, 100', // Default Gray
            phase: 0
        };

        const animate = () => {
            const width = canvas.width / dpr;
            const height = canvas.height / dpr;
            const centerX = width / 2;
            const centerY = height / 2;

            ctx.clearRect(0, 0, width, height);

            // Analyze Audio
            let frequency = 0;
            if (analyser && (isListening || isSpeaking)) {
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(dataArray);
                const sum = dataArray.reduce((acc, val) => acc + val, 0);
                frequency = sum / dataArray.length;
            }

            // Update Orb Physics
            if (isThinking) {
                orb.color = '255, 255, 255';
                orb.radius = 40 + Math.sin(Date.now() / 100) * 5;
            } else if (isListening) {
                orb.color = '255, 255, 255';
                const targetRadius = 60 + (frequency / 3);
                orb.radius += (targetRadius - orb.radius) * 0.2;
            } else if (isSpeaking) {
                orb.color = '208, 188, 255'; // Primary Purple
                const targetRadius = 50 + (frequency / 2);
                orb.radius += (targetRadius - orb.radius) * 0.2;
            } else {
                // Idle
                orb.color = '50, 50, 50';
                orb.radius = 30 + Math.sin(Date.now() / 2000) * 2;
            }

            // Draw Glow
            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, orb.radius * 2.5);
            gradient.addColorStop(0, `rgba(${orb.color}, 0.8)`);
            gradient.addColorStop(0.5, `rgba(${orb.color}, 0.2)`);
            gradient.addColorStop(1, `rgba(${orb.color}, 0)`);

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(centerX, centerY, orb.radius * 3, 0, Math.PI * 2);
            ctx.fill();

            // Draw Core
            ctx.fillStyle = `rgba(255, 255, 255, ${isThinking ? 0.9 : 0.8})`;
            ctx.beginPath();
            ctx.arc(centerX, centerY, isThinking ? 10 : orb.radius * 0.3, 0, Math.PI * 2);
            ctx.fill();

            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(animationRef.current);
            window.removeEventListener('resize', resize);
        };
    }, [isListening, isSpeaking, isThinking, analyser]);

    return (
        <Box sx={{
            width: '100%',
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            position: 'relative'
        }}>
            <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
        </Box>
    );
};

// Optimize: Prevent unnecessary re-renders
export default React.memo(OrbVisualizer);
