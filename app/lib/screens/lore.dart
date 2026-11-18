import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

import '../content.dart';
import '../md.dart';

class LoreList extends StatelessWidget {
  final Content content;
  const LoreList({super.key, required this.content});

  @override
  Widget build(BuildContext context) {
    final th = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      children: [
        Text('Читать по порядку: Предтечи → Средние эпохи → Поздние эпохи. Катаклизмы — отдельная летопись.',
            style: th.textTheme.bodyMedium!.copyWith(color: th.colorScheme.onSurfaceVariant)),
        const SizedBox(height: 12),
        for (final d in content.lore)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Card(
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                leading: const Text('📜', style: TextStyle(fontSize: 26)),
                title: Text(d.title, style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Text(d.subtitle),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => LoreReader(doc: d))),
              ),
            ),
          ),
      ],
    );
  }
}

class LoreReader extends StatefulWidget {
  final LoreDoc doc;
  const LoreReader({super.key, required this.doc});
  @override
  State<LoreReader> createState() => _LoreReaderState();
}

class _LoreReaderState extends State<LoreReader> {
  List<MdBlock>? blocks;
  final scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    rootBundle.loadString(widget.doc.asset).then((s) => setState(() => blocks = parseMarkdown(s)));
  }

  @override
  void dispose() {
    scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final heads = (blocks ?? []).where((b) => b.type.index <= BlockType.h3.index).toList();
    return Scaffold(
      appBar: AppBar(title: Text(widget.doc.title)),
      endDrawer: heads.isEmpty
          ? null
          : Drawer(
              child: SafeArea(
                child: ListView(children: [
                  const ListTile(title: Text('Оглавление', style: TextStyle(fontWeight: FontWeight.w700))),
                  for (final h in heads)
                    Builder(
                      builder: (ctx) => ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.only(left: 16.0 + 12 * h.type.index, right: 12),
                        title: Text(h.text.replaceAll('*', ''),
                            style: TextStyle(fontWeight: h.type == BlockType.h3 ? FontWeight.w400 : FontWeight.w700)),
                        onTap: () {
                          Navigator.of(ctx).pop();
                          final c = h.key.currentContext;
                          if (c != null) Scrollable.ensureVisible(c, duration: const Duration(milliseconds: 300));
                        },
                      ),
                    ),
                ]),
              ),
            ),
      body: blocks == null ? const Center(child: CircularProgressIndicator()) : MdView(blocks: blocks!, controller: scroll),
    );
  }
}
