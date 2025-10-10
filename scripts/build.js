const fs = require("fs");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const partialsDir = path.join(rootDir, "partials");
const templatesDir = path.join(rootDir, "templates");

const includePattern = /{{>\s*([a-zA-Z0-9_\-\/]+)\s*}}/g;

const partials = fs.readdirSync(partialsDir).reduce((acc, file) => {
  if (path.extname(file) !== ".html") return acc;
  const name = path.basename(file, ".html");
  acc[name] = fs.readFileSync(path.join(partialsDir, file), "utf8");
  return acc;
}, {});

const renderTemplate = (content, stack = []) =>
  content.replace(includePattern, (match, name, offset) => {
    if (!partials[name]) {
      throw new Error(`Partial "${name}" not found while rendering ${stack[0] ?? "template"}.`);
    }
    if (stack.includes(name)) {
      throw new Error(`Circular partial include detected: ${[...stack, name].join(" -> ")}`);
    }
    const lineStart = content.lastIndexOf("\n", offset);
    const indentationSlice = lineStart === -1 ? content.slice(0, offset) : content.slice(lineStart + 1, offset);
    const indentationMatch = indentationSlice.match(/^[\t ]*/);
    const indentation = indentationMatch ? indentationMatch[0] : "";
    const renderedPartial = renderTemplate(partials[name], [...stack, name]);
    const lines = renderedPartial.split("\n");
    return lines
      .map((line, index) => {
        if (line.trim().length === 0) return "";
        const prefix = index === 0 ? "" : indentation;
        return prefix + line;
      })
      .join("\n");
  });

fs.readdirSync(templatesDir)
  .filter((file) => path.extname(file) === ".html")
  .forEach((file) => {
    const templatePath = path.join(templatesDir, file);
    const outputPath = path.join(rootDir, file);
    const template = fs.readFileSync(templatePath, "utf8");
    const rendered = renderTemplate(template, [file]);
    fs.writeFileSync(outputPath, rendered);
    console.log(`Built ${path.relative(rootDir, outputPath)}`);
  });
