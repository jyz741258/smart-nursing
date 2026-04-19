// ============================================
// Smart Nursing System - Speech Recognition Composable
// Uses Web Speech API for voice input
// ============================================

import { ref, onMounted, onUnmounted } from 'vue'

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionErrorEvent {
  error: string
  message: string
}

// Check browser support for speech recognition
const isSpeechRecognitionSupported = typeof window !== 'undefined' && 
  ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

// Check if getUserMedia is supported
const isGetUserMediaSupported = typeof navigator !== 'undefined' && 
  'mediaDevices' in navigator && 
  'getUserMedia' in navigator.mediaDevices

export function useSpeechRecognition() {
  const isListening = ref(false)
  const isSupported = ref(isSpeechRecognitionSupported)
  const isMicPermissionGranted = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const error = ref<string | null>(null)
  const isRequestingPermission = ref(false)

  // @ts-ignore
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  let recognition: any = null

  // 请求麦克风权限
  const requestMicrophonePermission = async (): Promise<boolean> => {
    if (!isGetUserMediaSupported) {
      error.value = '您的浏览器不支持麦克风访问'
      return false
    }

    if (isMicPermissionGranted.value) {
      return true
    }

    isRequestingPermission.value = true
    error.value = null

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // 停止所有轨道以释放麦克风
      stream.getTracks().forEach(track => track.stop())
      isMicPermissionGranted.value = true
      error.value = null
      return true
    } catch (err: any) {
      console.error('Microphone permission error:', err)
      isMicPermissionGranted.value = false
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        error.value = '麦克风权限被拒绝，请在浏览器设置中允许使用麦克风'
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        error.value = '未检测到麦克风设备，请检查设备连接'
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        error.value = '麦克风正在被其他应用使用，请关闭后再试'
      } else {
        error.value = `麦克风访问失败: ${err.message || err.name}`
      }
      return false
    } finally {
      isRequestingPermission.value = false
    }
  }

  // 初始化语音识别
  const initRecognition = () => {
    if (!isSupported.value) {
      error.value = '您的浏览器不支持语音识别'
      return
    }

    recognition = new SpeechRecognition()
    recognition.continuous = false // Stop after each phrase
    recognition.interimResults = true // Interim results
    recognition.lang = 'zh-CN' // Set to Chinese
    recognition.maxAlternatives = 1

    // Recording started
    recognition.onstart = () => {
      isListening.value = true
      error.value = null
      interimTranscript.value = ''
    }

    // Processing results
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = ''
      let interimTranscriptResult = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalTranscript += result[0].transcript
        } else {
          interimTranscriptResult += result[0].transcript
        }
      }

      if (finalTranscript) {
        transcript.value += finalTranscript
        interimTranscript.value = ''
      } else {
        interimTranscript.value = interimTranscriptResult
      }
    }

    // Speech ended
    recognition.onspeechend = () => {
      isListening.value = false
      // Add interim transcript to final
      if (interimTranscript.value) {
        transcript.value += interimTranscript.value
        interimTranscript.value = ''
      }
      if (recognition) {
        recognition.stop()
      }
    }

    // Speech recognition error
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error)
      isListening.value = false

      switch (event.error) {
        case 'no-speech':
          error.value = '未检测到语音，请再说一遍'
          break
        case 'audio-capture':
          error.value = '未检测到麦克风，请检查设备'
          break
        case 'not-allowed':
          error.value = '麦克风权限被拒绝，请点击下方按钮重新授权'
          break
        case 'network':
          error.value = '网络错误，请检查网络连接'
          break
        case 'aborted':
          error.value = null
          break
        default:
          error.value = `识别错误: ${event.error}`
      }
    }

    // Recognition ended
    recognition.onend = () => {
      isListening.value = false
    }
  }

  // Start voice input
  const startListening = async () => {
    if (!isSupported.value || !recognition) {
      error.value = '语音识别不可用'
      return
    }

    // 先请求麦克风权限
    const hasPermission = await requestMicrophonePermission()
    if (!hasPermission) {
      return
    }

    try {
      transcript.value = ''
      interimTranscript.value = ''
      error.value = null
      recognition.start()
    } catch (e) {
      console.error('Failed to start speech recognition:', e)
      error.value = '启动语音输入失败'
    }
  }

  // Stop voice input
  const stopListening = () => {
    if (recognition && isListening.value) {
      recognition.stop()
    }
  }

  // Clear transcript (keep final result)
  const clearTranscript = () => {
    transcript.value = ''
    interimTranscript.value = ''
    error.value = null
  }

  // Set recognition language
  const setLanguage = (lang: string) => {
    if (recognition) {
      recognition.lang = lang
    }
  }

  // 重新请求权限并重置错误状态
  const retryPermission = async () => {
    isMicPermissionGranted.value = false
    error.value = null
  }

  onMounted(() => {
    initRecognition()
  })

  onUnmounted(() => {
    if (recognition) {
      recognition.abort()
    }
  })

  return {
    isListening,
    isSupported,
    isMicPermissionGranted,
    isRequestingPermission,
    transcript,
    interimTranscript,
    error,
    startListening,
    stopListening,
    clearTranscript,
    setLanguage,
    retryPermission,
    requestMicrophonePermission
  }
}
