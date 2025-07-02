#!/bin/bash

# Hentikan eksekusi jika ada error
set -e

# Nama branch utama
OLD_BRANCH="master"
NEW_BRANCH="master"

echo "📁 Memulai proses reset branch '$OLD_BRANCH'..."

# Checkout ke orphan branch baru (tanpa history)
git checkout --orphan "$NEW_BRANCH-temp"

# Tambahkan semua file ke staging area
git add -A

# Buat pesan commit otomatis
DATE=$(date '+%Y-%m-%d %H:%M:%S')
RANDOM_NUMBER=$RANDOM
COMMIT_MESSAGE="$DATE #$RANDOM_NUMBER"

# Commit awal dengan pesan otomatis
git commit -m "$COMMIT_MESSAGE"

# Hapus branch lama
git branch -D "$OLD_BRANCH"

# Ganti nama branch baru jadi nama lama
git branch -m "$NEW_BRANCH"

# Force push ke remote
git push -f origin "$NEW_BRANCH"

echo "✅ Branch '$NEW_BRANCH' telah di-reset dengan commit: '$COMMIT_MESSAGE' dan dipush ke remote!"