/// Pure Dart implementation of the Verhoeff algorithm.
/// Used to validate 12-digit Indian Aadhaar numbers to eliminate false-positives.
class Verhoeff {
  static const List<List<int>> _d = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
  ];

  static const List<List<int>> _p = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
  ];

  static const List<int> _inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9];

  /// Validates whether a numeric string passes the Verhoeff checksum.
  static bool validate(String num) {
    final clean = num.replaceAll(RegExp(r'\D'), '');
    if (clean.length != 12) return false;

    int c = 0;
    final reversed = clean.split('').reversed.toList();
    for (int i = 0; i < reversed.length; i++) {
      final digit = int.tryParse(reversed[i]);
      if (digit == null) return false;
      c = _d[c][_p[i % 8][digit]];
    }
    return c == 0;
  }

  /// Calculates the checksum digit for a number sequence.
  static int generateChecksum(String num) {
    final clean = num.replaceAll(RegExp(r'\D'), '');
    int c = 0;
    final reversed = clean.split('').reversed.toList();
    for (int i = 0; i < reversed.length; i++) {
      final digit = int.tryParse(reversed[i]) ?? 0;
      c = _d[c][_p[(i + 1) % 8][digit]];
    }
    return _inv[c];
  }
}
