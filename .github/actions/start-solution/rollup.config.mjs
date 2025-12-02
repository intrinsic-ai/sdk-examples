// rollup.config.js
import commonjs from "@rollup/plugin-commonjs";
import { nodeResolve } from "@rollup/plugin-node-resolve";

export default [
  {
    // Config for the 'main' script
    input: "index.js",
    output: {
      file: "dist/index.js",
      format: "cjs", 
      sourcemap: true,
    },
    plugins: [commonjs(), nodeResolve({ preferBuiltins: true })],
  },
  {
    // Config for the 'post' script
    input: "teardown.js",
    output: {
      file: "dist/teardown.js",
      format: "cjs", 
      sourcemap: true,
    },
    plugins: [commonjs(), nodeResolve({ preferBuiltins: true })],
  }
];
