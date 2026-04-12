const fs = require('fs');
const path = require('path');

const files = fs.readdirSync('.')
  .filter(file => file.endsWith('.md') && file !== 'index.json')
  .sort()
  .reverse();

const index = {
  updated: "2026-04-13T07:00:00+08:00",
  files: []
};

files.forEach(file => {
  try {
    const content = fs.readFileSync(file, 'utf8');
    const frontmatterMatch = content.match(/^---\s*\n(.*?)\n---/s);
    if (frontmatterMatch) {
      const frontmatter = frontmatterMatch[1];
      const idMatch = frontmatter.match(/id:\s*(\S+)/);
      const dateMatch = frontmatter.match(/date:\s*(\S+)/);
      const titleZhMatch = frontmatter.match(/zh:\s*"(.+)"/);
      const titleEnMatch = frontmatter.match(/en:\s*"(.+)"/);
      const tagsMatch = frontmatter.match(/tags:\s*\n((?:\s+-\s+.*\n)*)/);

      const id = idMatch ? idMatch[1] : file.replace('.md', '');
      const date = dateMatch ? dateMatch[1] : null;
      const titleZh = titleZhMatch ? titleZhMatch[1] : "No Chinese Title";
      const titleEn = titleEnMatch ? titleEnMatch[1] : "No English Title";
      
      let tags = [];
      if (tagsMatch) {
        tags = tagsMatch[1].split('\n').filter(line => line.trim()).map(line => 
          line.replace(/^\s*-\s*/, '').trim()
        );
      }

      index.files.push({
        id: id,
        file: file,
        date: date,
        title: {
          zh: titleZh,
          en: titleEn
        },
        tags: tags
      });
    }
  } catch (err) {
    console.log(`Error processing ${file}:`, err.message);
  }
});

fs.writeFileSync('index.json', JSON.stringify(index, null, 2));
console.log(`Built index with ${index.files.length} files`);
