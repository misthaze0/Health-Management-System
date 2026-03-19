<template>
  <div ref="auroraContainer" class="aurora-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  colorStops: {
    type: Array,
    default: () => ['#1890ff', '#36cfc9', '#1890ff']
  },
  amplitude: {
    type: Number,
    default: 1.0
  },
  blend: {
    type: Number,
    default: 0.5
  },
  speed: {
    type: Number,
    default: 1.0
  }
})

const auroraContainer = ref(null)
let animationId = null
let gl = null
let program = null
let renderer = null

// 顶点着色器
const VERTEX_SHADER = `
  attribute vec2 position;
  void main() {
    gl_Position = vec4(position, 0.0, 1.0);
  }
`

// 片段着色器
const FRAGMENT_SHADER = `
  precision highp float;
  
  uniform float uTime;
  uniform float uAmplitude;
  uniform vec3 uColorStops[3];
  uniform vec2 uResolution;
  uniform float uBlend;
  
  vec3 permute(vec3 x) {
    return mod(((x * 34.0) + 1.0) * x, 289.0);
  }
  
  float snoise(vec2 v) {
    const vec4 C = vec4(
      0.211324865405187, 0.366025403784439,
      -0.577350269189626, 0.024390243902439
    );
    vec2 i = floor(v + dot(v, C.yy));
    vec2 x0 = v - i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod(i, 289.0);
    
    vec3 p = permute(
      permute(i.y + vec3(0.0, i1.y, 1.0))
      + i.x + vec3(0.0, i1.x, 1.0)
    );
    
    vec3 m = max(
      0.5 - vec3(
        dot(x0, x0),
        dot(x12.xy, x12.xy),
        dot(x12.zw, x12.zw)
      ),
      0.0
    );
    m = m * m;
    m = m * m;
    
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
    
    vec3 g;
    g.x = a0.x * x0.x + h.x * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
  }
  
  void main() {
    vec2 uv = gl_FragCoord.xy / uResolution;
    
    vec3 color1 = uColorStops[0];
    vec3 color2 = uColorStops[1];
    vec3 color3 = uColorStops[2];
    
    vec3 rampColor;
    if (uv.x < 0.5) {
      rampColor = mix(color1, color2, uv.x * 2.0);
    } else {
      rampColor = mix(color2, color3, (uv.x - 0.5) * 2.0);
    }
    
    float height = snoise(vec2(uv.x * 2.0 + uTime * 0.1, uTime * 0.25)) * 0.5 * uAmplitude;
    height = exp(height);
    height = (uv.y * 2.0 - height + 0.2);
    float intensity = 0.6 * height;
    
    float midPoint = 0.20;
    float auroraAlpha = smoothstep(midPoint - uBlend * 0.5, midPoint + uBlend * 0.5, intensity);
    
    vec3 auroraColor = intensity * rampColor;
    
    gl_FragColor = vec4(auroraColor * auroraAlpha, auroraAlpha);
  }
`

// 十六进制颜色转RGB
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? [
    parseInt(result[1], 16) / 255,
    parseInt(result[2], 16) / 255,
    parseInt(result[3], 16) / 255
  ] : [0, 0, 0]
}

onMounted(() => {
  if (!auroraContainer.value) return
  
  const canvas = document.createElement('canvas')
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.width = '100%'
  canvas.style.height = '100%'
  canvas.style.pointerEvents = 'none'
  auroraContainer.value.appendChild(canvas)
  
  gl = canvas.getContext('webgl', {
    alpha: true,
    premultipliedAlpha: true,
    antialias: true
  })
  
  if (!gl) {
    console.warn('WebGL not supported')
    return
  }
  
  gl.clearColor(0, 0, 0, 0)
  gl.enable(gl.BLEND)
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA)
  
  // 创建着色器
  function createShader(type, source) {
    const shader = gl.createShader(type)
    gl.shaderSource(shader, source)
    gl.compileShader(shader)
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(shader))
      gl.deleteShader(shader)
      return null
    }
    return shader
  }
  
  const vertexShader = createShader(gl.VERTEX_SHADER, VERTEX_SHADER)
  const fragmentShader = createShader(gl.FRAGMENT_SHADER, FRAGMENT_SHADER)
  
  if (!vertexShader || !fragmentShader) return
  
  // 创建程序
  program = gl.createProgram()
  gl.attachShader(program, vertexShader)
  gl.attachShader(program, fragmentShader)
  gl.linkProgram(program)
  
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error(gl.getProgramInfoLog(program))
    return
  }
  
  gl.useProgram(program)
  
  // 创建三角形覆盖整个屏幕
  const positions = new Float32Array([
    -1, -1,
    3, -1,
    -1, 3
  ])
  
  const buffer = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
  gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW)
  
  const positionLocation = gl.getAttribLocation(program, 'position')
  gl.enableVertexAttribArray(positionLocation)
  gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0)
  
  // 获取uniform位置
  const uTimeLocation = gl.getUniformLocation(program, 'uTime')
  const uAmplitudeLocation = gl.getUniformLocation(program, 'uAmplitude')
  const uColorStopsLocation = gl.getUniformLocation(program, 'uColorStops')
  const uResolutionLocation = gl.getUniformLocation(program, 'uResolution')
  const uBlendLocation = gl.getUniformLocation(program, 'uBlend')
  
  // 设置颜色
  const colorStopsArray = props.colorStops.map(hexToRgb)
  
  // 调整大小
  function resize() {
    if (!auroraContainer.value || !gl) return
    const width = auroraContainer.value.offsetWidth
    const height = auroraContainer.value.offsetHeight
    canvas.width = width
    canvas.height = height
    gl.viewport(0, 0, width, height)
    gl.uniform2f(uResolutionLocation, width, height)
  }
  
  resize()
  window.addEventListener('resize', resize)
  
  // 动画循环
  let startTime = Date.now()
  function animate() {
    if (!gl || !program) return
    
    const currentTime = (Date.now() - startTime) * 0.001 * props.speed
    
    gl.uniform1f(uTimeLocation, currentTime)
    gl.uniform1f(uAmplitudeLocation, props.amplitude)
    gl.uniform1f(uBlendLocation, props.blend)
    gl.uniform3fv(uColorStopsLocation, colorStopsArray.flat())
    
    gl.clear(gl.COLOR_BUFFER_BIT)
    gl.drawArrays(gl.TRIANGLES, 0, 3)
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
  
  // 清理函数
  onUnmounted(() => {
    window.removeEventListener('resize', resize)
    if (animationId) cancelAnimationFrame(animationId)
    if (gl) {
      gl.deleteProgram(program)
      gl.deleteShader(vertexShader)
      gl.deleteShader(fragmentShader)
    }
  })
})
</script>

<style scoped>
.aurora-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
