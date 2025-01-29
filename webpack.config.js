// Copyright [2019] [Integreat Project]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");
module.exports = {
  entry: {
    main: "./hospitool/static/src/index.ts",
  },
  output: {
    filename: "[name].[contenthash].js",
    path: path.resolve(__dirname, "hospitool/static/dist"),
    clean: true,
    assetModuleFilename: "assets/[name]-[hash][ext][query]",
  },
  module: {
    rules: [
      {
        test: /\.s[ac]ss$/i,
        use: [
          process.env.NODE_ENV !== "production" ? "style-loader" : MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
      },
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
              plugins: [
                [
                  "@babel/plugin-transform-react-jsx",
                  {
                    pragma: "h",
                    pragmaFrag: "Fragment",
                  },
                ],
              ],
            },
          },
          "ts-loader",
        ],
        exclude: /node_modules/,
      },
      {
        test: /\.jsx?$/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
              plugins: [
                [
                  "@babel/plugin-transform-react-jsx",
                  {
                    pragma: "h",
                    pragmaFrag: "Fragment",
                  },
                ],
              ],
            },
          },
        ],
        exclude: /node_modules\/(?!chart\.js|htmldiff-js)/,
      },
      {
        test: /\.(woff(2)?|ttf|eot|otf)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        type: "asset/resource",
      },
      {
        test: /\.(png|jpg|gif|svg)$/i,
        type: "asset/inline",
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },

  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].[contenthash].css",
      chunkFilename: "[id].[contenthash].css",
    }),
    new BundleTracker({ filename: "./hospitool/webpack-stats.json" }),
  ],
};
