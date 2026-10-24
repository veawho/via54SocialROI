export interface SingleAccountParams {
  brand?: string;
  product?: string;
  platform?: 'xiaohongshu' | 'douyin' | 'bilibili' | 'wechat_channels';
  followers?: number;
  budget?: number;
  price?: number;
}

export interface MatrixParams {
  brand?: string;
  product?: string;
  budget?: number;
  price?: number;
}

export declare function execSocialRoiCli(args?: string[], pythonBin?: string): Promise<Record<string, any>>;

declare const Via54SocialROIPlugin: {
  name: string;
  version: string;
  edition: string;
  mcpServerPath: string;
  skillPath: string;
  apply(ctx: any, config?: { pythonBin?: string }): void;
  evaluateSingleAccount(params?: SingleAccountParams, pythonBin?: string): Promise<Record<string, any>>;
  evaluateMatrix(params?: MatrixParams, pythonBin?: string): Promise<Record<string, any>>;
};

export default Via54SocialROIPlugin;
