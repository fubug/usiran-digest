const fs = require('fs');
const path = require('path');

// Get all digest files
const digestDir = './data/digest';
const files = fs.readdirSync(digestDir)
  .filter(f => f.endsWith('.md'))
  .map(f => {
    const filePath = path.join(digestDir, f);
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Extract frontmatter
    const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
    if (!frontmatterMatch) {
      console.log(`⚠️ No frontmatter in ${f}`);
      return null;
    }
    
    const frontmatter = frontmatterMatch[1];
    const lines = frontmatter.split('\n');
    const data = { id: '', date: '', tags: [], sources: [], title: { zh: '', en: '' } };
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('id:')) {
        data.id = trimmed.split(':')[1].trim().replace(/"/g, '');
      } else if (trimmed.startsWith('date:')) {
        data.date = trimmed.split(':')[1].trim().replace(/"/g, '');
      } else if (trimmed.startsWith('tags:')) {
        const tags = trimmed.split(':')[1].trim();
        data.tags = JSON.parse(tags.replace(/'/g, '"'));
      } else if (trimmed.startsWith('sources:')) {
        const sources = trimmed.split(':')[1].trim();
        data.sources = JSON.parse(sources.replace(/'/g, '"'));
      } else if (trimmed.startsWith('title:')) {
        const title = trimmed.split(':')[1].trim();
        data.title = JSON.parse(title.replace(/'/g, '"'));
      }
    });
    
    return {
      id: data.id,
      date: data.date,
      file: f,
      title: data.title,
      tags: data.tags,
      sources: data.sources.length
    };
  })
  .filter(Boolean)
  .sort((a, b) => new Date(b.date) - new Date(a.date));

// Generate index.json
const index = {
  updated: new Date().toISOString().replace('Z', '+08:00'),
  files: files
};

console.log('Generated index with', files.length, 'files:');
files.forEach(f => console.log(`  ${f.id} - ${f.file}`));

fs.writeFileSync('./data/digest/index.json', JSON.stringify(index, null, 2) + '\n');