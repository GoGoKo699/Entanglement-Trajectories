# Upload Instructions — GitHub Web Interface

This package is deliberately limited to fewer than 100 files, and every file is below GitHub's browser-upload size limit. No terminal commands are required.

## 1. Preserve the historical paper code

1. Open the current repository: `GoGoKo699/Random-Density-Matrix`.
2. Open the branch menu near the upper-left of the file list.
3. Create a new branch named `paper-2024-original` from the current `main` branch.
4. Return to `main`.

This preserves the original root scripts as an easy-to-browse branch in addition to the normal Git history.

## 2. Upload the corrected repository root

1. Unzip `Entanglement-Trajectories-GitHub-Upload.zip` on Ubuntu.
2. Open the extracted folder.
3. On GitHub, choose **Add file → Upload files**.
4. Select everything inside the extracted folder, including hidden files such as `.github` and `.gitignore`, and drag the selected contents into the upload area. Do **not** drag the enclosing folder itself.
5. Use this commit message:

   `Replace historical root with corrected entanglement-trajectories repository edition`

6. Commit directly to `main` after the historical branch has been created.

The package overwrites every old root script with a compatibility notice, so no manual deletion is required.

## 3. Rename the repository

After the upload succeeds:

1. Open **Settings**.
2. Change the repository name from `Random-Density-Matrix` to `Entanglement-Trajectories`.
3. Do not create a new repository later with the old name, because that would break GitHub's redirect from the historical URL.

## 4. Apply the discovery settings

Follow `GITHUB_SETTINGS.md` to add the About description, DOI homepage, topics, social-preview image, and release metadata.

## 5. Final visual check

Confirm that:

- the README title is `Entanglement Trajectories`;
- all five main figures render;
- displayed mathematics renders correctly;
- the **Cite this repository** link appears;
- the Actions tab starts the `repository-qa` workflow;
- the historical branch `paper-2024-original` remains available.
