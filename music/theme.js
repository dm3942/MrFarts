/* ThemeLoop - gapless background-music loop for the browser (Web Audio API).
 *
 *   const theme = new ThemeLoop('music/mr_farts_theme.wav');
 *   button.onclick = () => theme.play();   // browsers need a user gesture before audio starts
 *   theme.volume = 0.5;  theme.pause();  theme.play();  theme.stop();
 *
 * The file is decoded into an AudioBuffer and played with loop=true, so the loop point is
 * sample-accurate (an <audio loop> element usually leaves a small gap at the seam).
 * Falls back to an <audio> element if Web Audio is unavailable.
 */
class ThemeLoop {
  constructor(url, { volume = 0.7, fadeIn = 0.4, fadeOut = 0.25 } = {}) {
    this.url = url; this.fadeIn = fadeIn; this.fadeOut = fadeOut;
    this._volume = volume; this.buffer = null; this.source = null; this.playing = false;
    this._offset = 0; this._startedAt = 0;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) {
      this.ctx = new AC();
      this.gain = this.ctx.createGain(); this.gain.gain.value = 0;
      this.analyser = this.ctx.createAnalyser(); this.analyser.fftSize = 256;
      this.gain.connect(this.analyser); this.analyser.connect(this.ctx.destination);
      this._data = new Uint8Array(this.analyser.frequencyBinCount);
    } else {
      this.el = new Audio(url); this.el.loop = true; this.el.volume = volume;
    }
  }
  get volume() { return this._volume; }
  set volume(v) { this._volume = v; if (this.el) this.el.volume = v; else if (this.playing) this.gain.gain.setTargetAtTime(v, this.ctx.currentTime, 0.02); }
  async load() {
    if (this.buffer || this.el) return;
    const res = await fetch(this.url); if (!res.ok) throw new Error('theme: HTTP ' + res.status + ' for ' + this.url);
    this.buffer = await this.ctx.decodeAudioData(await res.arrayBuffer());
  }
  async play() {
    if (this.el) { this.el.play(); this.playing = true; return; }
    if (this.ctx.state === 'suspended') await this.ctx.resume();
    await this.load();
    if (this.playing) return;
    const src = this.ctx.createBufferSource(); src.buffer = this.buffer; src.loop = true; src.connect(this.gain);
    const t = this.ctx.currentTime; src.start(t, this._offset % this.buffer.duration);
    this.gain.gain.cancelScheduledValues(t); this.gain.gain.setValueAtTime(0, t); this.gain.gain.linearRampToValueAtTime(this._volume, t + this.fadeIn);
    this.source = src; this._startedAt = t - this._offset; this.playing = true;
  }
  pause() {
    if (this.el) { this.el.pause(); this.playing = false; return; }
    if (!this.playing) return;
    const t = this.ctx.currentTime, src = this.source;
    this._offset = (t - this._startedAt) % this.buffer.duration; this.playing = false; this.source = null;
    this.gain.gain.cancelScheduledValues(t); this.gain.gain.setValueAtTime(this.gain.gain.value, t); this.gain.gain.linearRampToValueAtTime(0, t + this.fadeOut);
    src.stop(t + this.fadeOut);
  }
  stop() { this.pause(); this._offset = 0; if (this.el) this.el.currentTime = 0; }
  get position() {
    if (this.el) return this.el.currentTime;
    if (!this.buffer) return 0;
    return (this.playing ? this.ctx.currentTime - this._startedAt : this._offset) % this.buffer.duration;
  }
  get level() {   // 0..1 rough output level for a VU meter
    if (!this.analyser || !this.playing) return 0;
    this.analyser.getByteTimeDomainData(this._data); let s = 0;
    for (const v of this._data) { const d = (v - 128) / 128; s += d * d; }
    return Math.sqrt(s / this._data.length);
  }
}
window.ThemeLoop = ThemeLoop;
