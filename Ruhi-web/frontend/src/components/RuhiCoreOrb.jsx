import React, { useEffect, useRef } from 'react';

export default function RuhiCoreOrb({ state = 'idle', size = 420 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let time = 0;

    // Set high-DPI resolution
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);

    const centerX = size / 2;
    const centerY = size / 2;

    // Particles array
    const particleCount = 45;
    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        angle: Math.random() * Math.PI * 2,
        radius: 60 + Math.random() * 85,
        speed: 0.005 + Math.random() * 0.012,
        size: 1.5 + Math.random() * 2.5,
        alpha: 0.2 + Math.random() * 0.7,
        pulseOffset: Math.random() * Math.PI * 2,
      });
    }

    const render = () => {
      time += state === 'thinking' ? 0.04 : 0.015;
      ctx.clearRect(0, 0, size, size);

      // 1. Ambient Glow Field
      const ambientGrad = ctx.createRadialGradient(
        centerX, centerY, 10,
        centerX, centerY, size * 0.48
      );
      ambientGrad.addColorStop(0, 'rgba(0, 242, 254, 0.25)');
      ambientGrad.addColorStop(0.4, 'rgba(121, 40, 202, 0.15)');
      ambientGrad.addColorStop(0.8, 'rgba(79, 172, 254, 0.05)');
      ambientGrad.addColorStop(1, 'rgba(5, 7, 12, 0)');
      
      ctx.fillStyle = ambientGrad;
      ctx.beginPath();
      ctx.arc(centerX, centerY, size * 0.48, 0, Math.PI * 2);
      ctx.fill();

      // 2. Orbital Rings (Dynamic Breathing)
      const ringCount = 3;
      for (let i = 0; i < ringCount; i++) {
        const ringBaseRadius = 70 + i * 32;
        const wobble = Math.sin(time * 1.5 + i * 1.2) * 5;
        const currentRadius = ringBaseRadius + wobble;

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate((time * (i % 2 === 0 ? 0.3 : -0.2)) + (i * Math.PI / 4));

        ctx.beginPath();
        ctx.ellipse(0, 0, currentRadius, currentRadius * 0.92, 0, 0, Math.PI * 2);
        ctx.strokeStyle = i === 0 
          ? 'rgba(0, 242, 254, 0.5)' 
          : i === 1 
            ? 'rgba(168, 85, 247, 0.4)' 
            : 'rgba(79, 172, 254, 0.3)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([8, 12 + i * 4]);
        ctx.stroke();
        ctx.restore();
      }

      // 3. Neural Node Particles
      particles.forEach((p, idx) => {
        p.angle += p.speed * (state === 'thinking' ? 2.5 : 1);
        const dynamicRadius = p.radius + Math.sin(time * 2 + p.pulseOffset) * 6;
        const px = centerX + Math.cos(p.angle) * dynamicRadius;
        const py = centerY + Math.sin(p.angle) * dynamicRadius;

        // Draw node
        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fillStyle = idx % 3 === 0 
          ? `rgba(0, 242, 254, ${p.alpha})` 
          : `rgba(168, 85, 247, ${p.alpha})`;
        ctx.fill();

        // Connect nearby nodes subtly
        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const p2x = centerX + Math.cos(p2.angle) * p2.radius;
          const p2y = centerY + Math.sin(p2.angle) * p2.radius;
          const dist = Math.hypot(px - p2x, py - p2y);

          if (dist < 55) {
            ctx.beginPath();
            ctx.moveTo(px, py);
            ctx.lineTo(p2x, p2y);
            ctx.strokeStyle = `rgba(0, 242, 254, ${(1 - dist / 55) * 0.18})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      });

      // 4. Inner Intelligent Core
      const corePulse = Math.sin(time * 2.5) * 4;
      const coreRadius = 38 + (state === 'thinking' ? Math.sin(time * 6) * 6 : corePulse);

      const coreGrad = ctx.createRadialGradient(
        centerX, centerY, 0,
        centerX, centerY, coreRadius
      );
      coreGrad.addColorStop(0, '#ffffff');
      coreGrad.addColorStop(0.2, '#00f2fe');
      coreGrad.addColorStop(0.7, '#7928ca');
      coreGrad.addColorStop(1, 'rgba(121, 40, 202, 0)');

      ctx.save();
      ctx.shadowColor = '#00f2fe';
      ctx.shadowBlur = state === 'thinking' ? 35 : 20;

      ctx.beginPath();
      ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
      ctx.fillStyle = coreGrad;
      ctx.fill();

      // Core Diamond Center
      ctx.beginPath();
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(time * 0.8);
      ctx.rect(-10, -10, 20, 20);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fill();
      ctx.restore();

      ctx.restore();

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [state, size]);

  return (
    <div className="canvas-orb-container" style={{ width: size, height: size }}>
      <canvas
        ref={canvasRef}
        className="canvas-orb"
        style={{ width: size, height: size }}
      />
      <div className="orb-overlay-status">
        <span className="hero-badge-pulse" />
        <span>RUHI CORE // {state.toUpperCase()}</span>
      </div>
    </div>
  );
}
