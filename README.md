# Tofik AI Photo V2

Python/Kivy offline Android photo editor starter.

## Included and working offline
- Photo selection and preview
- Auto enhance using Pillow
- 2x Lanczos resize (not AI super-resolution)
- Portrait tone adjustment (not AI face restoration)
- Soft beauty filter
- Cartoon effect
- Black & white and sepia
- Reset and save

## Not implemented as true AI in this build
- Background removal requires a segmentation model.
- Object removal requires a user mask plus an inpainting model.
- True AI upscaling and face restoration require compatible on-device ML models.
The UI labels these honestly instead of silently returning fake AI results. The app itself does not need internet for included tools.

## Build APK with GitHub Actions
1. Extract this ZIP.
2. Create a GitHub repository and upload the extracted files/folders (including `.github`).
3. Open Actions and run "Build Tofik AI Photo V2 APK".
4. Download the `Tofik-AI-Photo-V2-APK` artifact from the completed workflow.
5. Extract the artifact ZIP and install the APK on your Android phone.

This is a debug APK for testing. Building requires GitHub Actions/Linux; no APK has been built or tested on a physical device yet.
