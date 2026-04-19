// ============================================
// 智慧养老系统 - 音效管理系统
// 使用 Web Audio API 生成程序化音效
// ============================================

type SoundType = 'success' | 'error' | 'warning' | 'info' | 'click' | 'notification' | 'complete'

class AudioManager {
  private audioContext: AudioContext | null = null
  private enabled: boolean = true
  private volume: number = 0.5
  private initialized: boolean = false

  // 初始化音频上下文
  private initContext() {
    if (this.initialized) return

    try {
      this.audioContext = new AudioContext()
      this.initialized = true
    } catch (e) {
      console.warn('Web Audio API 不支持', e)
    }
  }

  // 初始化并恢复上下文（浏览器策略要求用户交互后才能播放）
  async init(): Promise<void> {
    this.initContext()

    if (this.audioContext?.state === 'suspended') {
      await this.audioContext.resume()
    }
  }

  // 启用/禁用音效
  setEnabled(enabled: boolean) {
    this.enabled = enabled
    localStorage.setItem('smart-nursing-sound-enabled', enabled.toString())
  }

  // 设置音量 (0-1)
  setVolume(volume: number) {
    this.volume = Math.max(0, Math.min(1, volume))
    localStorage.setItem('smart-nursing-sound-volume', volume.toString())
  }

  // 获取状态
  isEnabled(): boolean {
    return this.enabled
  }

  getVolume(): number {
    return this.volume
  }

  // 加载用户偏好
  loadPreferences() {
    const savedEnabled = localStorage.getItem('smart-nursing-sound-enabled')
    const savedVolume = localStorage.getItem('smart-nursing-sound-volume')

    if (savedEnabled !== null) {
      this.enabled = savedEnabled === 'true'
    }

    if (savedVolume !== null) {
      this.volume = parseFloat(savedVolume)
    }
  }

  // ========================
  // 音效生成器
  // ========================

  // 成功音效（清脆的上行音）
  playSuccess() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    // 正弦波 + 高频起始
    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(523.25, now) // C5
    oscillator.frequency.exponentialRampToValueAtTime(1046.5, now + 0.1) // C6

    // 音量包络
    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(this.volume * 0.3, now + 0.02)
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.3)

    oscillator.start(now)
    oscillator.stop(now + 0.3)
  }

  // 错误音效（低沉的下行音）
  playError() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.type = 'sawtooth'
    oscillator.frequency.setValueAtTime(200, now)
    oscillator.frequency.exponentialRampToValueAtTime(100, now + 0.2)

    // 低通滤波器让声音更沉闷
    const filter = this.audioContext.createBiquadFilter()
    filter.type = 'lowpass'
    filter.frequency.value = 800
    oscillator.disconnect()
    oscillator.connect(filter)
    filter.connect(gainNode)

    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(this.volume * 0.4, now + 0.02)
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.25)

    oscillator.start(now)
    oscillator.stop(now + 0.25)
  }

  // 警告音效（中频颤音）
  playWarning() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.type = 'triangle'
    oscillator.frequency.setValueAtTime(440, now) // A4
    oscillator.frequency.linearRampToValueAtTime(550, now + 0.15) // C#5

    // 颤音效果
    const lfo = this.audioContext.createOscillator()
    lfo.frequency.value = 8
    const lfoGain = this.audioContext.createGain()
    lfoGain.gain.value = 20
    lfo.connect(lfoGain)
    lfoGain.connect(oscillator.frequency)

    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(this.volume * 0.3, now + 0.05)
    gainNode.gain.linearRampToValueAtTime(0, now + 0.3)

    oscillator.start(now)
    oscillator.stop(now + 0.3)
    lfo.start(now)
    lfo.stop(now + 0.3)
  }

  // 信息提示音（短促的高频）
  playInfo() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.type = 'sine'
    oscillator.frequency.value = 800

    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(this.volume * 0.2, now + 0.01)
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.1)

    oscillator.start(now)
    oscillator.stop(now + 0.1)
  }

  // 点击音效（轻微反馈）
  playClick() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.type = 'sine'
    oscillator.frequency.value = 600

    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(this.volume * 0.15, now + 0.005)
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.05)

    oscillator.start(now)
    oscillator.stop(now + 0.05)
  }

  // 通知音效（类似消息提示）
  playNotification() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const notes = [523.25, 659.25, 783.99] // C5, E5, G5 - 大三和弦

    notes.forEach((freq, i) => {
      const oscillator = this.audioContext!.createOscillator()
      const gainNode = this.audioContext!.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(this.audioContext!.destination)

      oscillator.type = 'sine'
      oscillator.frequency.value = freq

      const startTime = now + i * 0.08
      gainNode.gain.setValueAtTime(0, startTime)
      gainNode.gain.linearRampToValueAtTime(this.volume * 0.2, startTime + 0.02)
      gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + 0.25)

      oscillator.start(startTime)
      oscillator.stop(startTime + 0.25)
    })
  }

  // 完成音效（成功达成目标）
  playComplete() {
    if (!this.enabled || !this.audioContext) return

    const now = this.audioContext.currentTime
    const notes = [
      523.25, 659.25, 783.99, 1046.5 // C大调上行
    ]

    notes.forEach((freq, i) => {
      const oscillator = this.audioContext!.createOscillator()
      const gainNode = this.audioContext!.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(this.audioContext!.destination)

      oscillator.type = 'sine'
      oscillator.frequency.value = freq

      const startTime = now + i * 0.12
      gainNode.gain.setValueAtTime(0, startTime)
      gainNode.gain.linearRampToValueAtTime(this.volume * 0.25, startTime + 0.03)
      gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + 0.4)

      oscillator.start(startTime)
      oscillator.stop(startTime + 0.4)
    })
  }

  // 播放指定类型的音效
  play(type: SoundType) {
    switch (type) {
      case 'success':
        this.playSuccess()
        break
      case 'error':
        this.playError()
        break
      case 'warning':
        this.playWarning()
        break
      case 'info':
        this.playInfo()
        break
      case 'click':
        this.playClick()
        break
      case 'notification':
        this.playNotification()
        break
      case 'complete':
        this.playComplete()
        break
    }
  }

  // ========================
  // 语音合成 - Text to Speech
  // ========================

  // 检查语音合成是否支持
  isSpeechSynthesisSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window
  }

  // 说话（语音合成）
  speak(text: string, options?: {
    lang?: string
    rate?: number
    pitch?: number
    volume?: number
  }): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isSpeechSynthesisSupported()) {
        reject(new Error('Speech synthesis not supported'))
        return
      }

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = options?.lang || 'zh-CN'
      utterance.rate = options?.rate || 1.0
      utterance.pitch = options?.pitch || 1.0
      utterance.volume = (options?.volume !== undefined ? options.volume : this.volume) * 2

      utterance.onend = () => resolve()
      utterance.onerror = (e) => reject(e)

      window.speechSynthesis.speak(utterance)
    })
  }

  // 停止说话
  stopSpeaking(): void {
    if (this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel()
    }
  }

  // 检查是否正在说话
  isSpeaking(): boolean {
    return this.isSpeechSynthesisSupported() && window.speechSynthesis.speaking
  }

  // 语音反馈（播放提示音+说话）
  async playAndSpeak(text: string, soundType: SoundType = 'info'): Promise<void> {
    this.play(soundType)
    await this.speak(text)
  }

  // 语音确认（用户操作成功）
  async speakSuccess(text: string = '操作成功'): Promise<void> {
    this.playSuccess()
    await this.speak(text)
  }

  // 语音警告
  async speakWarning(text: string): Promise<void> {
    this.playWarning()
    await this.speak(text)
  }

  // 语音错误提示
  async speakError(text: string = '操作失败'): Promise<void> {
    this.playError()
    await this.speak(text)
  }
}

// 导出单例
export const audioManager = new AudioManager()

// 自动加载偏好设置
audioManager.loadPreferences()
