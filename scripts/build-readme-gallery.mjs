// Compatibility entry: the refinement builder preserves the original SVG geometry.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const args=[fileURLToPath(new URL('./build-readme-gallery.py',import.meta.url))];
if(process.argv[2])args.push('--output',process.argv[2]);
const result=spawnSync(process.env.PYTHON || 'python3',args,{stdio:'inherit'});
if(result.error)throw result.error;
process.exit(result.status ?? 1);
