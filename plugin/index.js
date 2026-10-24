/**
 * @via54/plugin-social-roi — Universal Node.js / Cordis / Agent Plugin Adapter
 * 跨框架 Node.js / Cordis / OpenClaw 插件入口 (Trial & Base Architecture Edition)
 *
 * Bridges JavaScript/TypeScript Agent runtimes (Cordis, Koishi, OpenClaw, LangChain.js)
 * to the via54SocialROI Python CLI & MCP Server.
 */

const { execFile } = require('child_process');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const CLI_PATH = path.join(REPO_ROOT, 'cli.py');
const MCP_PATH = path.join(REPO_ROOT, 'mcp_server.py');

/**
 * Execute a via54SocialROI CLI command and return parsed JSON.
 * @param {string[]} args CLI arguments
 * @param {string} [pythonBin='python'] Python executable
 * @returns {Promise<object>}
 */
function execSocialRoiCli(args = [], pythonBin = process.env.PYTHON_BIN || 'python') {
  return new Promise((resolve, reject) => {
    execFile(
      pythonBin,
      [CLI_PATH, ...args, '--json'],
      { cwd: REPO_ROOT, maxBuffer: 10 * 1024 * 1024, encoding: 'utf8' },
      (err, stdout, stderr) => {
        if (err) {
          return reject(new Error(`via54SocialROI CLI error: ${stderr || err.message}`));
        }
        try {
          resolve(JSON.parse(stdout.trim()));
        } catch (parseErr) {
          resolve({ rawOutput: stdout.trim(), stderr: stderr.trim() });
        }
      }
    );
  });
}

/**
 * Cordis / Koishi / OpenClaw standard plugin export
 */
const Via54SocialROIPlugin = {
  name: 'via54-social-roi',
  version: '2.5.0',
  edition: 'OPEN_CORE_DEMO',
  mcpServerPath: MCP_PATH,
  skillPath: path.join(REPO_ROOT, 'via54socialroi', 'SKILL.md'),

  apply(ctx, config = {}) {
    const pythonBin = config.pythonBin || 'python';

    if (ctx && typeof ctx.command === 'function') {
      ctx
        .command('social-roi.evaluate <brand:string> <product:string>', 'Evaluate single-account Social ROI & 8-LLM GEO')
        .option('platform', '-p <platform:string>', { fallback: 'xiaohongshu' })
        .option('followers', '-f <followers:number>', { fallback: 100000 })
        .option('budget', '-b <budget:number>', { fallback: 15000 })
        .option('price', '-r <price:number>', { fallback: 299 })
        .action(async ({ options }, brand, product) => {
          return await execSocialRoiCli(
            [
              '--brand', brand || 'DemoBrand',
              '--product', product || 'HeroProduct',
              '--platform', options.platform,
              '--followers', String(options.followers),
              '--budget', String(options.budget),
              '--price', String(options.price),
            ],
            pythonBin
          );
        });

      ctx
        .command('social-roi.matrix <brand:string> <product:string>', 'Evaluate multi-account matrix allocation & ROI')
        .option('budget', '-b <budget:number>', { fallback: 120000 })
        .option('price', '-r <price:number>', { fallback: 299 })
        .action(async ({ options }, brand, product) => {
          return await execSocialRoiCli(
            [
              '--matrix',
              '--brand', brand || 'DemoBrand',
              '--product', product || 'HeroProduct',
              '--budget', String(options.budget),
              '--price', String(options.price),
            ],
            pythonBin
          );
        });
    }
  },

  evaluateSingleAccount(params = {}, pythonBin = 'python') {
    const args = [
      '--brand', params.brand || 'DemoBrand',
      '--product', params.product || 'HeroProduct',
      '--platform', params.platform || 'xiaohongshu',
      '--followers', String(params.followers || 100000),
      '--budget', String(params.budget || 15000),
      '--price', String(params.price || 299),
    ];
    return execSocialRoiCli(args, pythonBin);
  },

  evaluateMatrix(params = {}, pythonBin = 'python') {
    const args = [
      '--matrix',
      '--brand', params.brand || 'DemoBrand',
      '--product', params.product || 'HeroProduct',
      '--budget', String(params.budget || 120000),
      '--price', String(params.price || 299),
    ];
    return execSocialRoiCli(args, pythonBin);
  },
};

module.exports = Via54SocialROIPlugin;
module.exports.default = Via54SocialROIPlugin;
module.exports.execSocialRoiCli = execSocialRoiCli;
