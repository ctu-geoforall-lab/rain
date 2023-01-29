# Steps

Clone https://github.com/gisquick/gisquick

```
git clone https://github.com/gisquick/gisquick.git
cd gisquick/clients/gisquick-web
```

Copy source files of custom InfoPanel into `src/extensions/` directory

Install dependencies
```
npm install
npm install d3
```

Build JavaScript module
```
CSS_EXTRACT=False npm run build -- --target lib --formats umd-min --dest dist/ --name rain src/extensions/RainChart.vue
```

Open page with project settings on Gisquick page, go to the layers section and open attribute table settings. Upload `dist/rain.umd.min.js` file and assign RainChart component to selected layers.
