// localStorage layer: named templates, each with a version history.
export interface PromptDoc {
  system: string;
  user: string;
  fewShot: { input: string; output: string }[];
  jsonMode: boolean;
}
export interface Version { ts: number; doc: PromptDoc; }
export interface Template { id: string; name: string; versions: Version[]; }

const KEY = "prompt-lab-templates";

export function loadTemplates(): Template[] {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "[]"); }
  catch { return []; }
}

export function saveTemplates(list: Template[]): void {
  localStorage.setItem(KEY, JSON.stringify(list));
}

// Save (or update) a template, pushing a new revision onto its history (cap 20).
export function upsertTemplate(list: Template[], name: string, doc: PromptDoc): Template[] {
  const version: Version = { ts: Date.now(), doc };
  const existing = list.find((t) => t.name === name);
  if (existing) {
    existing.versions = [version, ...existing.versions].slice(0, 20);
    return [...list];
  }
  return [{ id: "tpl_" + Date.now().toString(36), name, versions: [version] }, ...list];
}