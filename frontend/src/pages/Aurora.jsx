import { useEffect, useRef } from 'react'

// Cada capa es una "cortina" de luz. Colores: [borde inferior, medio, punta] en RGB.
const CAPAS = [
  { base: 0.62, alto: 0.62, onda: 0.06,  vel: 1.0,  fase: 0.0, alpha: 0.85, rayos: 0.05,  colores: ['90,255,165', '40,215,190', '140,90,255'] },
  { base: 0.54, alto: 0.55, onda: 0.05,  vel: 0.75, fase: 2.1, alpha: 0.65, rayos: 0.034, colores: ['60,240,200', '60,160,255', '190,90,255'] },
  { base: 0.68, alto: 0.46, onda: 0.045, vel: 1.25, fase: 4.2, alpha: 0.55, rayos: 0.062, colores: ['120,255,140', '50,230,170', '80,140,255'] },
  { base: 0.46, alto: 0.42, onda: 0.04,  vel: 0.6,  fase: 5.5, alpha: 0.45, rayos: 0.028, colores: ['90,200,255', '160,100,255', '255,120,200'] },
  { base: 0.80, alto: 0.50, onda: 0.05,  vel: 0.9,  fase: 1.2, alpha: 0.5,  rayos: 0.045, colores: ['150,255,120', '50,220,180', '120,110,255'] },
]

const ALTO_SPRITE = 256

// Franja vertical de 1px con el degradado de la cortina: se estira luego con drawImage (barato).
function crearSprite(capa, nuevoCanvas) {
  const c = nuevoCanvas(1, ALTO_SPRITE)
  const g = c.getContext('2d')
  const [abajo, medio, arriba] = capa.colores
  const grad = g.createLinearGradient(0, 0, 0, ALTO_SPRITE)
  grad.addColorStop(0,    `rgba(${arriba},0)`)
  grad.addColorStop(0.30, `rgba(${arriba},0.22)`)
  grad.addColorStop(0.60, `rgba(${medio},0.5)`)
  grad.addColorStop(0.84, `rgba(${abajo},0.9)`)
  grad.addColorStop(0.92, `rgba(${abajo},1)`)
  grad.addColorStop(1,    `rgba(${abajo},0)`)
  g.fillStyle = grad
  g.fillRect(0, 0, 1, ALTO_SPRITE)
  return c
}

function dibujar(ctx, sprites, W, H, t) {
  ctx.clearRect(0, 0, W, H)
  ctx.globalCompositeOperation = 'lighter'
  const paso = 2

  CAPAS.forEach((capa, i) => {
    const s = t * capa.vel * 0.6
    for (let x = 0; x < W; x += paso) {
      const u = x / W

      // Zonas que se intensifican y se apagan, desplazándose lentamente
      const env = Math.pow(0.5 + 0.5 * Math.sin(u * 4.2 + s * 0.35 + capa.fase), 1.6)
      const borde = Math.pow(Math.sin(Math.PI * u), 0.6)

      // Borde inferior ondulante
      const y = H * capa.base
        + Math.sin(u * 7 + s * 0.55 + capa.fase) * H * capa.onda
        + Math.sin(u * 17 - s * 0.4 + capa.fase * 1.7) * H * capa.onda * 0.45

      // Altura variable de la cortina
      const h = H * capa.alto * (0.6 + 0.4 * Math.sin(u * 5 + s * 0.5 + capa.fase * 1.3)) * (0.4 + 0.6 * env)

      // Rayos verticales que titilan
      const k = x * capa.rayos
      const rayo = 0.72
        + 0.24 * Math.sin(k + s * 1.1 + capa.fase)
        + 0.18 * Math.sin(k * 2.31 - s * 1.7 + 1.7)
        + 0.12 * Math.sin(k * 4.77 + s * 0.9 + 3.1)

      const a = 1.2 * capa.alpha * rayo * (0.25 + 0.75 * env) * borde
      ctx.globalAlpha = Math.min(1, Math.max(0, a))
      ctx.drawImage(sprites[i], 0, 0, 1, ALTO_SPRITE, x, y - h, paso, h)
    }
  })

  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
}

export default function Aurora() {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const nuevo = (w, h) => {
      const c = document.createElement('canvas')
      c.width = w
      c.height = h
      return c
    }
    const sprites = CAPAS.map((c) => crearSprite(c, nuevo))
    const reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let W = 0
    let H = 0
    let raf = 0
    const inicio = performance.now()

    // Se dibuja a baja resolución (el CSS lo estira y suaviza): mucho más ligero
    const ajustar = () => {
      const escala = window.innerWidth < 600 ? 0.35 : 0.5
      W = Math.max(1, Math.round(window.innerWidth * escala))
      H = Math.max(1, Math.round(window.innerHeight * escala))
      canvas.width = W
      canvas.height = H
      if (reducido) dibujar(ctx, sprites, W, H, 20)
    }

    const cuadro = (ahora) => {
      dibujar(ctx, sprites, W, H, 20 + (ahora - inicio) / 1000)
      raf = requestAnimationFrame(cuadro)
    }

    ajustar()
    window.addEventListener('resize', ajustar)
    if (!reducido) raf = requestAnimationFrame(cuadro)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', ajustar)
    }
  }, [])

  return (
    <div className="aurora-bg" aria-hidden="true">
      <span className="aurora-stars aurora-stars-far" />
      <span className="aurora-stars" />
      <canvas ref={ref} className="aurora-canvas" />
    </div>
  )
}