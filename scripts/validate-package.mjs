import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const root = process.cwd();
const skill = join(root, "skills", "prepare-nz-visa-translations");
const required = [
  "SKILL.md",
  "agents/openai.yaml",
  "assets/translator-profile.example.json",
  "assets/vector-page-template.html",
  "references/document-patterns.md",
  "references/layout-reconstruction.md",
  "references/translation-and-qa.md",
  "scripts/assemble_translation_pdf.py",
  "scripts/render_html_to_pdf.py",
  "scripts/validate_translation_pdf.py",
  "requirements.txt"
];

for (const relative of required) {
  const path = join(skill, relative);
  if (!existsSync(path)) throw new Error(`Missing required file: ${relative}`);
}

const markdown = readFileSync(join(skill, "SKILL.md"), "utf8");
if (!/^---\n[\s\S]*?\n---\n/.test(markdown)) {
  throw new Error("SKILL.md does not contain valid-looking YAML frontmatter");
}
if (!/^name:\s*prepare-nz-visa-translations\s*$/m.test(markdown)) {
  throw new Error("SKILL.md name does not match the directory name");
}
if (!/^description:\s*\S+/m.test(markdown)) {
  throw new Error("SKILL.md is missing a description");
}

const privateProfile = join(skill, "assets", "translator-profile.json");
if (existsSync(privateProfile)) {
  throw new Error("Private translator-profile.json must not be included in the public package");
}

const exampleProfile = JSON.parse(
  readFileSync(join(skill, "assets", "translator-profile.example.json"), "utf8")
);
const expectedPlaceholders = {
  name: "Translator Full Name",
  telephone: "+00 000 0000 0000",
  address: "Translator's full postal address",
  qualification: "Relevant qualifications and experience showing competence in Chinese and English."
};
for (const [key, value] of Object.entries(expectedPlaceholders)) {
  if (exampleProfile[key] !== value) {
    throw new Error(`Translator profile example must keep the public placeholder for: ${key}`);
  }
}

const python = process.env.PYTHON || "python3";
const cache = mkdtempSync(join(tmpdir(), "prepare-nz-visa-translations-"));
try {
  execFileSync(python, [
    "-m",
    "py_compile",
    join(skill, "scripts", "assemble_translation_pdf.py"),
    join(skill, "scripts", "render_html_to_pdf.py"),
    join(skill, "scripts", "validate_translation_pdf.py")
  ], {
    stdio: "inherit",
    env: { ...process.env, PYTHONPYCACHEPREFIX: cache }
  });
} finally {
  rmSync(cache, { recursive: true, force: true });
}

console.log("Package validation passed.");
