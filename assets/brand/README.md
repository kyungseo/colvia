# Colvia brand assets

The selected symbol is R6-1, Open C. Use **Colvia** as the name and **AI Work Harness** as an introduction descriptor. The C opens into a continuing path; the bend recalls a pass between ridges. Earlier exploration names remain historical proposals, not additional product names.

## Files and use

| Use | Asset |
| --- | --- |
| Logo on a light / dark background | `logo-light.svg` / `logo-dark.svg` |
| Centered README introduction | `logo-hero-light.svg` / `logo-hero-dark.svg` |
| First introduction with descriptor | `logo-intro-light.svg` / `logo-intro-dark.svg` |
| Monochrome / inherited color | `symbol-black.svg`, `symbol-white.svg`, `symbol-current.svg` |
| App icon, both themes | `icon.svg`, `png/icon-*.png` |
| Native packaging | `colvia.icns` (macOS), `colvia.ico` (Windows) |

All final SVGs contain outlined shapes and need no installed font. Keep the symbol's proportions and open end; do not add fading dots, stripes, gradients or a second theme-specific app tile. Use the supplied viewBox as the clear-space box. At 16–32 pixels use the provided raster/icon files and inspect the actual size. Palette: teal `#1F5F5B`, ivory `#F6F1E7`, mint `#8CC6BC` for dark-document symbols. The app tile stays teal/ivory.

## Editable source and regeneration

`source/r6-1-open-c.svg` is the exact selected centerline source; `source/geometry.json` freezes outlined symbol and wordmark paths. `source/outline.swift` can regenerate geometry on macOS with CoreGraphics/CoreText and the bundled Inter OTFs, registered for that process only. It refuses font substitution. It does not install fonts globally. Preserve the selected source and inspect any changed glyph or geometry result before replacing it.

The source-only Node builder needs **sharp 0.35.5**. Install that dependency in a build environment, or set `COLVIA_SHARP_MODULE` to its module location, then run `node scripts/build-brand-assets.mjs` from this checkout. An optional first argument selects a separate output directory. It never downloads inputs. The generated manifest records input/output hashes and the full renderer version set. Byte reproducibility applies to that renderer set; another platform/library combination must be validated rather than assumed identical. Final users do not need Node, sharp, Swift or Inter installed.

To regenerate geometry on macOS, run `swift assets/brand/source/outline.swift assets/brand/source/r6-1-open-c.svg` and review the JSON output before replacing `source/geometry.json`. Release-time icon builds consume only generated assets from the trusted source tree. These build inputs are not part of the managed project runtime inventory.

## Font and history

Inter 4.1 Medium and SemiBold are unmodified upstream fonts under the SIL Open Font License 1.1. See [font license](source/LICENSE.txt) and [version, upstream URL and hashes](source/PROVENANCE.json). The logo artwork is covered by the repository's [Apache-2.0 license](../../LICENSE); the bundled font files retain their own license. Consult those licenses for their terms.

The [development record](../../docs/development/CHORE-20261105-003-brand-and-agent-entry.md) records selection and implementation status. Complete exploratory originals are retained in private design history; this directory carries the selected original and reproducible production sources. Installed root documentation remains text-only; the repository's English and Korean front pages use the light/dark logo assets.

Native display still needs platform observation. An embedded Windows executable/window icon does not establish the icon Windows shows for an unpackaged notification. The Windows management package now includes a pinned PNG and icon-aware registry recovery. Actual notification attribution and final-candidate macOS/Windows display checks remain separate from generating valid files.

## Windows resource build

The source release builder copies the target-specific `rsrc_windows_amd64.syso` or `rsrc_windows_arm64.syso` into its private build directory and builds that package. Normal end-user execution does not compile resources. Regenerate both objects with:

```sh
python3 scripts/build-windows-icon.py --icon assets/brand/colvia.ico --output distribution/windows
```

The generator writes one `.rsrc` COFF section with eight PNG icon payloads and neutral-language icon group101. Refresh `distribution/windows/icon-resources.json` from the validated ICO, notification PNG256 and generated objects when intentionally changing the icon. The linked-PE test uses Go's independent `debug/pe` parser to verify both architectures and all payload bytes. It uses a synthetic runtime archive and does not certify a downloadable installer or native Windows display.

Deferred Windows display checks include large/small shared icon selection, system scaling on high-DPI displays and unpackaged notification attribution. Native observations must use the exact final candidate; a successful cross-compile does not establish these results.

## README gallery

The [README diagrams](../../manual/assets/gallery/README.md) refine the preserved source illustrations. Run `python3 scripts/build-readme-gallery.py` to regenerate the Korean/English and light/dark variants. They use the outlined brand paths, center the symbol and wordmark by their actual bounds, and retain the original diagrams’ roles and connections. Text remains editable and uses embedded, licensed font subsets for viewing without installed fonts.
