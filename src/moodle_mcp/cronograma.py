"""Estado local do cronograma: só ids e datas, nunca texto do Moodle (ADR-0003, ADR-0018).

Guarda, por aluno e por Moodle, o prazo de cada tarefa na última leitura registrada, para a tool
`mudancas_de_cronograma` dizer o que mudou. Nomes, descrições e qualquer outro conteúdo ficam de fora:
os nomes que aparecem na resposta vêm sempre da leitura atual.

- Arquivo `moodle-mcp/cronograma.json` no diretório de dados do usuário (XDG_DATA_HOME, LOCALAPPDATA
  ou ~/.local/share), com permissão 0600; a escrita é atômica (arquivo temporário e renomeação).
- Chave = URL base do Moodle + id do aluno: trocar de conta ou de semestre não mistura leituras.
- Arquivo ausente, corrompido ou de outra versão vale como "sem leitura anterior".
- Só guarda prazos de até DIAS_GUARDADOS dias atrás: o que ficou mais antigo não interessa e sairia da
  resposta do Moodle sem ter sido removido.
"""

import json
import os
import tempfile
from pathlib import Path

DIAS_GUARDADOS = 30
VERSAO = 1

Prazos = dict[int, int]  # id da tarefa → prazo (timestamp)
Mudanca = tuple[int, str, int | None, int | None]  # (id, tipo, prazo antes, prazo agora)


def arquivo() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    return Path(base) / "moodle-mcp" / "cronograma.json"


def _chave(url: str, userid: int) -> str:
    return f"{url}|{userid}"


def _leituras() -> dict[str, dict]:
    try:
        dados = json.loads(arquivo().read_text(encoding="utf-8"))
        leituras = dados["leituras"] if dados["versao"] == VERSAO else None
    except (OSError, ValueError, KeyError, TypeError):
        return {}
    return leituras if isinstance(leituras, dict) else {}


def ler(url: str, userid: int) -> tuple[int, Prazos] | None:
    """(instante, prazos) da última leitura registrada, ou None se não há leitura válida."""
    try:
        leitura = _leituras()[_chave(url, userid)]
        return int(leitura["lida_em"]), {int(k): int(v) for k, v in leitura["prazos"].items()}
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def salvar(url: str, userid: int, lida_em: int, prazos: Prazos) -> bool:
    """Registra a leitura. Devolve False (sem levantar erro) se o arquivo não puder ser escrito."""
    leituras = _leituras()
    leituras[_chave(url, userid)] = {"lida_em": lida_em, "prazos": {str(k): v for k, v in prazos.items()}}
    destino = arquivo()
    temporario = None
    try:
        destino.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temporario = tempfile.mkstemp(dir=destino.parent, suffix=".tmp")  # já nasce com permissão 0600
        with os.fdopen(fd, "w", encoding="utf-8") as saida:
            json.dump({"versao": VERSAO, "leituras": leituras}, saida)
        os.replace(temporario, destino)
        return True
    except OSError:
        if temporario is not None:
            try:
                os.unlink(temporario)
            except OSError:
                pass
        return False


def comparar(antes: Prazos, depois: Prazos) -> list[Mudanca]:
    """Prazos adiados, adiantados, novos e removidos (sem prazo ou fora da resposta) entre duas leituras."""
    mudancas: list[Mudanca] = []
    for id_, novo in depois.items():
        antigo = antes.get(id_)
        if antigo is None:
            mudancas.append((id_, "novo", None, novo))
        elif novo != antigo:
            mudancas.append((id_, "adiado" if novo > antigo else "adiantado", antigo, novo))
    mudancas += [(id_, "removido", antigo, None) for id_, antigo in antes.items() if id_ not in depois]
    return mudancas
