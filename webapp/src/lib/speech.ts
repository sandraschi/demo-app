export function stripMarkdown(md: string): string {
  return md
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[*_`#~]/g, "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/\n+/g, " ")
    .trim();
}

export function speak(text: string, onEnd?: () => void): () => void {
  if (typeof window === "undefined" || !window.speechSynthesis) return () => {};
  const plain = stripMarkdown(text);
  if (!plain) return () => {};
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(plain);
  u.rate = 1;
  u.pitch = 1;
  if (onEnd) u.onend = onEnd;
  window.speechSynthesis.speak(u);
  return () => window.speechSynthesis.cancel();
}

export function isTTSSupported(): boolean {
  return typeof window !== "undefined" && !!window.speechSynthesis;
}