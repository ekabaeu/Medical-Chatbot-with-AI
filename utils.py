def escape_csv(s):
    """Mengamankan string untuk dimasukkan ke dalam sel CSV."""
    if not s:
        return '""'
    # Jika string mengandung koma, kutip ganda, atau newline, bungkus dengan kutip ganda
    # dan ganti setiap kutip ganda di dalam string dengan dua kutip ganda.
    if ',' in s or '"' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s
