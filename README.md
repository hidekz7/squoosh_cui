# [Squoosh]!

[Squoosh] is an image compression web app that reduces image sizes through numerous formats.

# Privacy

Squoosh does not send your image to a server. All image compression processes locally.

However, Squoosh utilizes Google Analytics to collect the following:

- [Basic visitor data](https://support.google.com/analytics/answer/6004245?ref_topic=2919631).
- The before and after image size value.
- If Squoosh PWA, the type of Squoosh installation.
- If Squoosh PWA, the installation time and date.

# Developing

To develop for Squoosh:

1. Clone the repository
1. To install node packages, run:
   ```sh
   npm install
   ```
1. Then build the app by running:
   ```sh
   npm run build
   ```
1. After building, start the development server by running:
   ```sh
   npm run dev
   ```

# Local CUI (no Node.js)

If you want to use Squoosh as a local CUI program without Node.js, use the
Python script below. It compresses images locally using Pillow.

```sh
python -m pip install Pillow
python cui/squoosh_cui.py input.jpg output.jpg --format jpeg --quality 75
```

For PNG optimization:

```sh
python cui/squoosh_cui.py input.png output.png --format png --optimize
```

# Local GUI (no Node.js)

You can also use a lightweight GUI that wraps the CUI program. It supports
multiple-file drag-and-drop (via `tkinterdnd2`), output folder selection, and a
side-by-side preview for quality tuning.

```sh
python -m pip install Pillow tkinterdnd2
python cui/squoosh_gui.py
```

# Contributing

Squoosh is an open-source project that appreciates all community involvement. To contribute to the project, follow the [contribute guide](/CONTRIBUTING.md).

[squoosh]: https://squoosh.app
