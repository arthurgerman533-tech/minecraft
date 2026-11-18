import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

class Kicker extends StatelessWidget {
  final String text;
  const Kicker(this.text, {super.key});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: 20, bottom: 8),
        child: Text(text.toUpperCase(),
            style: TextStyle(
                color: Theme.of(context).colorScheme.primary, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1.6)),
      );
}

class CmdChip extends StatelessWidget {
  final String cmd;
  const CmdChip(this.cmd, {super.key});
  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: () {
        Clipboard.setData(ClipboardData(text: cmd));
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(SnackBar(content: Text('Скопировано: $cmd'), duration: const Duration(seconds: 1)));
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
            color: cs.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: cs.outlineVariant)),
        child: Text(cmd, style: const TextStyle(fontFamily: 'monospace', fontSize: 13)),
      ),
    );
  }
}

Widget cmdWrap(List<String> cmds) =>
    Wrap(spacing: 6, runSpacing: 6, children: [for (final c in cmds) CmdChip(c)]);

Future<void> openUrl(BuildContext context, String url) async {
  final ok = url.isNotEmpty && await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
  if (!ok && context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ссылка появится перед открытием сервера')));
  }
}
