BASH_COMPLETION = """
# ytt bash completion script
_ytt_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="-h --help -o --output -f --format -l --lang -t --translate -c --copy --no-timestamps --no-metadata --chunk-size --search --template --list-langs --combine -q --quiet -m --manual -v --version"

    case "${prev}" in
        -f|--format)
            COMPREPLY=( $(compgen -W "markdown llm text json jsonl srt vtt" -- "${cur}") )
            return 0
            ;;
        --template)
            COMPREPLY=( $(compgen -W "summary qna takeaways flashcards" -- "${cur}") )
            return 0
            ;;
        -o|--output)
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}

complete -F _ytt_completions ytt ytx yt-transcript yt2md yt2text
"""

ZSH_COMPLETION = """
#compdef ytt ytx yt-transcript yt2md yt2text

_ytt() {
    local -a opts
    opts=(
        '-h[Show help]'
        '--help[Show help]'
        '-o[Output file or directory]:file:_files'
        '--output[Output file or directory]:file:_files'
        '-f[Output format]:format:(markdown llm text json jsonl srt vtt)'
        '--format[Output format]:format:(markdown llm text json jsonl srt vtt)'
        '-l[Language code]:lang:'
        '-t[Translate language]:lang:'
        '-c[Copy to clipboard]'
        '--no-timestamps[Remove timestamps]'
        '--combine[Combine transcripts into single file]'
        '--search[Search term inside transcript]:query:'
        '--template[AI Prompt Template]:template:(summary qna takeaways flashcards)'
        '-m[Show interactive manual]'
        '--manual[Show interactive manual]'
        '-v[Show version]'
    )
    _describe -t commands 'ytt' opts
}

_ytt "$@"
"""

def generate_completion(shell: str) -> str:
    s = shell.lower().strip()
    if s == "bash":
        return BASH_COMPLETION.strip()
    elif s == "zsh":
        return ZSH_COMPLETION.strip()
    else:
        raise ValueError("Supported shell completions: bash, zsh")
