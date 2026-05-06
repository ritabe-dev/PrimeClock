import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { RotateCcw } from 'lucide-react';
import './styles.css';

const TWO_PI = Math.PI * 2;
const TWELVE = -Math.PI / 2;
const TICK_EASE_SECONDS = 0.14;
const BIRTH_HIGHLIGHT_SECONDS = 1.25;
const BIRTH_HIGHLIGHT_HOLD_SECONDS = 0.33;

function isPrime(value) {
  if (value < 2) return false;
  if (value === 2) return true;
  if (value % 2 === 0) return false;
  const limit = Math.floor(Math.sqrt(value));
  for (let factor = 3; factor <= limit; factor += 2) {
    if (value % factor === 0) return false;
  }
  return true;
}

function colorForPrime(prime) {
  const hue = (prime * 137.508) % 360;
  return {
    hue,
    stroke: `hsla(${hue}, 88%, 68%, 0.88)`,
    fill: `hsla(${hue}, 92%, 62%, 0.34)`,
    glow: `hsla(${hue}, 98%, 70%, 0.72)`
  };
}

function formatElapsed(seconds) {
  return String(Math.floor(seconds));
}

function angleDistance(a, b) {
  return Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b)));
}

function easeOutCubic(value) {
  return 1 - Math.pow(1 - value, 3);
}

function easeOutSine(value) {
  return Math.sin((value * Math.PI) / 2);
}

function steppedAngleForHand(hand, wholeSecond) {
  const tickAge = Math.max(0, wholeSecond - hand.bornAt);
  const phase = (tickAge % hand.prime) / hand.prime;
  return TWELVE + phase * TWO_PI;
}

function interpolateAngle(from, to, progress) {
  const delta = Math.atan2(Math.sin(to - from), Math.cos(to - from));
  return from + delta * progress;
}

function PrimeClockCanvas({ running, resetKey, onStatsChange }) {
  const canvasRef = useRef(null);
  const shellRef = useRef(null);
  const animationRef = useRef(0);
  const startTimeRef = useRef(null);
  const elapsedRef = useRef(0);
  const lastSecondRef = useRef(-1);
  const primesRef = useRef([]);
  const pointerRef = useRef(null);
  const [hovered, setHovered] = useState(null);

  const resetClock = useCallback(() => {
    startTimeRef.current = running ? performance.now() : null;
    elapsedRef.current = 0;
    lastSecondRef.current = -1;
    primesRef.current = [];
    setHovered(null);
    onStatsChange({ elapsed: 0, latestPrime: null, primeCount: 0 });
  }, [onStatsChange, running]);

  useEffect(() => {
    resetClock();
  }, [resetKey, resetClock]);

  useEffect(() => {
    if (running && startTimeRef.current === null) {
      startTimeRef.current = performance.now() - elapsedRef.current * 1000;
    }
    if (!running) {
      startTimeRef.current = null;
      lastSecondRef.current = Math.floor(elapsedRef.current);
    }
  }, [running]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const shell = shellRef.current;
    if (!canvas || !shell) return undefined;

    function resizeCanvas() {
      const rect = shell.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
    }

    const resizeObserver = new ResizeObserver(resizeCanvas);
    resizeObserver.observe(shell);
    resizeCanvas();

    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const ctx = canvas.getContext('2d');

    function drawDial(now) {
      if (running && startTimeRef.current !== null) {
        elapsedRef.current = (now - startTimeRef.current) / 1000;
      }

      const elapsed = elapsedRef.current;
      const currentWholeSecond = Math.floor(elapsed + 0.000001);
      for (let second = lastSecondRef.current + 1; second <= currentWholeSecond; second += 1) {
        if (isPrime(second) && !primesRef.current.some((hand) => hand.prime === second)) {
          primesRef.current.push({
            prime: second,
            bornAt: second,
            color: colorForPrime(second)
          });
        }
      }
      lastSecondRef.current = Math.max(lastSecondRef.current, currentWholeSecond);

      onStatsChange({
        elapsed,
        latestPrime: primesRef.current.at(-1)?.prime ?? null,
        primeCount: primesRef.current.length
      });

      const dpr = window.devicePixelRatio || 1;
      const width = canvas.width / dpr;
      const height = canvas.height / dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      const cx = width / 2;
      const cy = height / 2;
      const radius = Math.min(width, height) * 0.43;
      const innerRadius = Math.max(10, radius * 0.055);

      drawBackground(ctx, cx, cy, radius);
      drawTicks(ctx, cx, cy, radius);
      drawPrimeHands(ctx, cx, cy, radius, innerRadius, elapsed, currentWholeSecond, pointerRef.current);
      drawTwelveSlit(ctx, cx, cy, radius);
      drawCenterCore(ctx, cx, cy, radius);

      animationRef.current = requestAnimationFrame(drawDial);
    }

    animationRef.current = requestAnimationFrame(drawDial);
    return () => cancelAnimationFrame(animationRef.current);
  }, [onStatsChange, running]);

  function drawBackground(ctx, cx, cy, radius) {
    const outer = ctx.createRadialGradient(cx, cy, radius * 0.02, cx, cy, radius * 1.18);
    outer.addColorStop(0, 'rgba(25, 27, 20, 0.24)');
    outer.addColorStop(0.52, 'rgba(10, 12, 12, 0.6)');
    outer.addColorStop(0.88, 'rgba(4, 5, 7, 0.95)');
    outer.addColorStop(1, 'rgba(1, 1, 2, 0)');
    ctx.fillStyle = outer;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.18, 0, TWO_PI);
    ctx.fill();

    ctx.save();
    ctx.strokeStyle = 'rgba(230, 236, 244, 0.36)';
    ctx.lineWidth = 1.35;
    ctx.shadowColor = 'rgba(255, 255, 255, 0.22)';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, TWO_PI);
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
    ctx.lineWidth = radius * 0.003;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.72, 0, TWO_PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.42, 0, TWO_PI);
    ctx.stroke();
    ctx.restore();
  }

  function drawTicks(ctx, cx, cy, radius) {
    ctx.save();
    ctx.strokeStyle = 'rgba(234, 239, 246, 0.58)';
    ctx.lineCap = 'round';
    for (let index = 0; index < 60; index += 1) {
      const angle = TWELVE + (index / 60) * TWO_PI;
      const major = index % 5 === 0;
      const start = radius * (major ? 0.942 : 0.968);
      const end = radius * 0.988;
      ctx.lineWidth = major ? 1.75 : 1;
      ctx.globalAlpha = major ? 0.88 : 0.54;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(angle) * start, cy + Math.sin(angle) * start);
      ctx.lineTo(cx + Math.cos(angle) * end, cy + Math.sin(angle) * end);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawPrimeHands(ctx, cx, cy, radius, innerRadius, elapsed, currentWholeSecond, pointer) {
    let nextHovered = null;
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.965, 0, TWO_PI);
    ctx.clip();
    ctx.globalCompositeOperation = 'lighter';
    primesRef.current.forEach((hand, index) => {
      const age = Math.max(0, elapsed - hand.bornAt);
      const targetAngle = steppedAngleForHand(hand, currentWholeSecond);
      const previousAngle = steppedAngleForHand(hand, Math.max(hand.bornAt, currentWholeSecond - 1));
      const tickProgress = Math.min(1, Math.max(0, elapsed - currentWholeSecond) / TICK_EASE_SECONDS);
      const centerAngle = interpolateAngle(previousAngle, targetAngle, easeOutCubic(tickProgress));
      const halfWidth = Math.PI / hand.prime;
      const isFresh = age < 1.2;
      const isTicking = tickProgress < 1 && targetAngle !== previousAngle;
      const recency = primesRef.current.length <= 1 ? 1 : index / (primesRef.current.length - 1);
      const ageFade = 0.62 + recency * 0.28;
      const birthPulse = isFresh ? 1 + (1 - age / 1.2) * 0.9 : 1;
      const alpha = Math.min(0.72, 0.12 + ageFade * 0.3) * birthPulse;
      const outerRadius = radius * 0.965;
      const birthProgress = Math.min(
        1,
        Math.max(0, age - BIRTH_HIGHLIGHT_HOLD_SECONDS) /
          (BIRTH_HIGHLIGHT_SECONDS - BIRTH_HIGHLIGHT_HOLD_SECONDS)
      );
      const birthIntensity = 1 - easeOutSine(birthProgress);
      const isLatest = index === primesRef.current.length - 1;
      const latestBoost = isLatest ? birthIntensity : 0;

      if (pointer) {
        const dx = pointer.x - cx;
        const dy = pointer.y - cy;
        const pointerRadius = Math.hypot(dx, dy);
        const pointerAngle = Math.atan2(dy, dx);
        if (
          pointerRadius >= innerRadius &&
          pointerRadius <= radius * 0.985 &&
          angleDistance(pointerAngle, centerAngle) <= halfWidth
        ) {
          nextHovered = hand.prime;
        }
      }

      if (isTicking) {
        ctx.save();
        const ghostAlpha = (1 - tickProgress) * alpha * 0.34;
        const ghostGradient = ctx.createRadialGradient(cx, cy, innerRadius, cx, cy, outerRadius);
        ghostGradient.addColorStop(0, `hsla(${hand.color.hue}, 98%, 72%, 0.34)`);
        ghostGradient.addColorStop(0.46, `hsla(${hand.color.hue}, 92%, 62%, 0.16)`);
        ghostGradient.addColorStop(1, `hsla(${hand.color.hue}, 90%, 58%, 0.01)`);
        ctx.globalAlpha = ghostAlpha;
        ctx.fillStyle = ghostGradient;
        ctx.shadowColor = hand.color.glow;
        ctx.shadowBlur = 28;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(previousAngle - halfWidth) * innerRadius, cy + Math.sin(previousAngle - halfWidth) * innerRadius);
        ctx.arc(cx, cy, outerRadius, previousAngle - halfWidth, previousAngle + halfWidth);
        ctx.lineTo(cx + Math.cos(previousAngle + halfWidth) * innerRadius, cy + Math.sin(previousAngle + halfWidth) * innerRadius);
        ctx.arc(cx, cy, innerRadius, previousAngle + halfWidth, previousAngle - halfWidth, true);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
      }

      ctx.save();
      ctx.globalAlpha = Math.min(0.2, alpha * 0.34 + latestBoost * 0.12);
      const auraGradient = ctx.createRadialGradient(cx, cy, innerRadius, cx, cy, outerRadius);
      auraGradient.addColorStop(0, `hsla(${hand.color.hue}, 96%, 74%, 0.24)`);
      auraGradient.addColorStop(0.48, `hsla(${hand.color.hue}, 92%, 62%, 0.11)`);
      auraGradient.addColorStop(1, `hsla(${hand.color.hue}, 90%, 58%, 0)`);
      ctx.fillStyle = auraGradient;
      ctx.filter = 'blur(8px)';
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(centerAngle - halfWidth) * innerRadius, cy + Math.sin(centerAngle - halfWidth) * innerRadius);
      ctx.arc(cx, cy, outerRadius, centerAngle - halfWidth, centerAngle + halfWidth);
      ctx.lineTo(cx + Math.cos(centerAngle + halfWidth) * innerRadius, cy + Math.sin(centerAngle + halfWidth) * innerRadius);
      ctx.arc(cx, cy, innerRadius, centerAngle + halfWidth, centerAngle - halfWidth, true);
      ctx.closePath();
      ctx.fill();
      ctx.filter = 'none';

      const handFlashAlpha = Math.min(1, alpha + 0.14 + latestBoost * 0.48);
      ctx.globalAlpha = handFlashAlpha;
      const sectorGradient = ctx.createRadialGradient(cx, cy, innerRadius, cx, cy, outerRadius);
      sectorGradient.addColorStop(0, `hsla(${hand.color.hue}, 98%, ${70 + latestBoost * 8}%, ${0.72 + latestBoost * 0.24})`);
      sectorGradient.addColorStop(0.38, `hsla(${hand.color.hue}, 94%, ${62 + latestBoost * 8}%, ${0.34 + latestBoost * 0.42})`);
      sectorGradient.addColorStop(1, `hsla(${hand.color.hue}, 92%, 56%, ${0.04 + latestBoost * 0.24})`);
      ctx.fillStyle = sectorGradient;
      ctx.shadowColor = hand.color.glow;
      ctx.shadowBlur = (isFresh ? 42 : 22) + latestBoost * 82;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(centerAngle - halfWidth) * innerRadius, cy + Math.sin(centerAngle - halfWidth) * innerRadius);
      ctx.arc(cx, cy, outerRadius, centerAngle - halfWidth, centerAngle + halfWidth);
      ctx.lineTo(cx + Math.cos(centerAngle + halfWidth) * innerRadius, cy + Math.sin(centerAngle + halfWidth) * innerRadius);
      ctx.arc(cx, cy, innerRadius, centerAngle + halfWidth, centerAngle - halfWidth, true);
      ctx.closePath();
      ctx.fill();

      ctx.globalAlpha = handFlashAlpha;
      ctx.strokeStyle = hand.color.stroke;
      ctx.lineWidth = (isFresh ? 2.2 : 1.05) + latestBoost * 3.6;
      ctx.shadowBlur = (isFresh ? 28 : 10) + latestBoost * 62;
      ctx.stroke();

      if (latestBoost > 0) {
        ctx.globalAlpha = latestBoost * 0.34;
        ctx.strokeStyle = `hsla(${hand.color.hue}, 98%, 74%, 0.96)`;
        ctx.lineWidth = Math.max(2, radius * 0.004);
        ctx.shadowColor = hand.color.glow;
        ctx.shadowBlur = 20 + latestBoost * 42;
        ctx.beginPath();
        ctx.arc(cx, cy, outerRadius, centerAngle - halfWidth, centerAngle + halfWidth);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(centerAngle - halfWidth) * innerRadius, cy + Math.sin(centerAngle - halfWidth) * innerRadius);
        ctx.lineTo(cx + Math.cos(centerAngle - halfWidth) * outerRadius, cy + Math.sin(centerAngle - halfWidth) * outerRadius);
        ctx.moveTo(cx + Math.cos(centerAngle + halfWidth) * innerRadius, cy + Math.sin(centerAngle + halfWidth) * innerRadius);
        ctx.lineTo(cx + Math.cos(centerAngle + halfWidth) * outerRadius, cy + Math.sin(centerAngle + halfWidth) * outerRadius);
        ctx.stroke();

        ctx.globalAlpha = latestBoost * 0.42;
        ctx.fillStyle = sectorGradient;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(centerAngle - halfWidth) * innerRadius, cy + Math.sin(centerAngle - halfWidth) * innerRadius);
        ctx.arc(cx, cy, outerRadius, centerAngle - halfWidth, centerAngle + halfWidth);
        ctx.lineTo(cx + Math.cos(centerAngle + halfWidth) * innerRadius, cy + Math.sin(centerAngle + halfWidth) * innerRadius);
        ctx.arc(cx, cy, innerRadius, centerAngle + halfWidth, centerAngle - halfWidth, true);
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
    });
    ctx.restore();

    setHovered((current) => (current === nextHovered ? current : nextHovered));
  }

  function drawTwelveSlit(ctx, cx, cy, radius) {
    const topY = cy - radius;
    const innerY = cy + radius * 0.035;
    const beamWidth = Math.max(20, radius * 0.068);
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, TWO_PI);
    ctx.clip();
    ctx.globalCompositeOperation = 'lighter';

    const verticalFade = ctx.createLinearGradient(cx, topY, cx, innerY);
    verticalFade.addColorStop(0, 'rgba(255, 245, 182, 0.5)');
    verticalFade.addColorStop(0.16, 'rgba(255, 232, 118, 0.42)');
    verticalFade.addColorStop(0.6, 'rgba(255, 219, 89, 0.18)');
    verticalFade.addColorStop(1, 'rgba(255, 208, 72, 0)');

    const horizontalFade = ctx.createLinearGradient(cx - beamWidth, 0, cx + beamWidth, 0);
    horizontalFade.addColorStop(0, 'rgba(255, 214, 68, 0)');
    horizontalFade.addColorStop(0.36, 'rgba(255, 224, 82, 0.06)');
    horizontalFade.addColorStop(0.48, 'rgba(255, 246, 182, 0.22)');
    horizontalFade.addColorStop(0.5, 'rgba(255, 255, 235, 0.48)');
    horizontalFade.addColorStop(0.52, 'rgba(255, 246, 182, 0.22)');
    horizontalFade.addColorStop(0.64, 'rgba(255, 224, 82, 0.06)');
    horizontalFade.addColorStop(1, 'rgba(255, 214, 68, 0)');

    ctx.save();
    ctx.globalAlpha = 0.66;
    ctx.filter = 'blur(8px)';
    ctx.fillStyle = verticalFade;
    ctx.fillRect(cx - beamWidth * 0.52, topY, beamWidth * 1.04, innerY - topY);
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.68;
    ctx.filter = 'blur(5px)';
    ctx.fillStyle = horizontalFade;
    ctx.fillRect(cx - beamWidth, topY, beamWidth * 2, innerY - topY);
    ctx.restore();

    const coreGradient = ctx.createLinearGradient(cx, topY, cx, innerY);
    coreGradient.addColorStop(0, 'rgba(255, 255, 245, 1)');
    coreGradient.addColorStop(0.44, 'rgba(255, 232, 118, 0.96)');
    coreGradient.addColorStop(0.82, 'rgba(255, 222, 84, 0.42)');
    coreGradient.addColorStop(1, 'rgba(255, 222, 84, 0.02)');
    ctx.strokeStyle = coreGradient;
    ctx.shadowColor = 'rgba(255, 226, 105, 0.95)';
    ctx.shadowBlur = 14;
    ctx.lineWidth = Math.max(1.4, radius * 0.0038);
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(cx, topY);
    ctx.lineTo(cx, innerY);
    ctx.stroke();

    ctx.globalAlpha = 0.24;
    ctx.shadowBlur = 22;
    ctx.lineWidth = Math.max(3, radius * 0.008);
    ctx.stroke();
    ctx.restore();
  }

  function drawCenterCore(ctx, cx, cy, radius) {
    const core = ctx.createRadialGradient(cx, cy, 1, cx, cy, radius * 0.068);
    core.addColorStop(0, 'rgba(0, 0, 0, 1)');
    core.addColorStop(0.58, 'rgba(5, 8, 14, 0.98)');
    core.addColorStop(1, 'rgba(40, 56, 72, 0.3)');
    ctx.save();
    ctx.fillStyle = core;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.056, 0, TWO_PI);
    ctx.fill();
    ctx.strokeStyle = 'rgba(208, 226, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();
  }

  const updatePointer = useCallback((event) => {
    const rect = canvasRef.current.getBoundingClientRect();
    pointerRef.current = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  }, []);

  const clearPointer = useCallback(() => {
    pointerRef.current = null;
    setHovered(null);
  }, []);

  return (
    <div className="clock-shell" ref={shellRef}>
      <canvas
        ref={canvasRef}
        className="prime-canvas"
        aria-label="Prime clock visualization"
        onPointerMove={updatePointer}
        onPointerLeave={clearPointer}
      />
      {hovered && (
        <div className="hover-readout">
          <span>p={hovered}</span>
          <span>{hovered}s cycle</span>
        </div>
      )}
    </div>
  );
}

function App() {
  const [running, setRunning] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const [stats, setStats] = useState({ elapsed: 0, latestPrime: null, primeCount: 0 });

  const controlsLabel = running ? 'running' : 'start';
  const statsItems = useMemo(
    () => [
      ['elapsed', formatElapsed(stats.elapsed)],
      ['latest prime', stats.latestPrime ?? '—'],
      ['prime count', stats.primeCount]
    ],
    [stats]
  );

  function reset() {
    setRunning(false);
    setResetKey((key) => key + 1);
  }

  return (
    <main className="app-frame">
      <div className="clock-stage">
        <PrimeClockCanvas running={running} resetKey={resetKey} onStatsChange={setStats} />
      </div>

      <div className="control-strip" aria-label="Prime clock controls">
        <button className="start-button" type="button" onClick={() => setRunning(true)} disabled={running} aria-label={controlsLabel} />
        <button className="icon-button" type="button" onClick={reset} aria-label="Reset prime clock" title="Reset">
          <RotateCcw size={15} strokeWidth={1.8} />
        </button>
        <div className="stats-row" aria-live="polite">
          {statsItems.map(([label, value]) => (
            <div className="stat" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
