# --- Dicionário de Traduções ---
translations = {
    'pt': {
        'page_title': "Dawkins’ Weasel Program",
        'main_title': "🧬 Dawkins’ Weasel Program",
        'description': """
Esta aplicação demonstra o "Weasel Program", um experimento mental de Richard Dawkins. 
O objetivo é mostrar como a seleção cumulativa pode gerar resultados complexos a partir do acaso e da seleção.
Começando com uma frase aleatória, o programa gera cópias com uma pequena chance de mutação em cada geração e seleciona a cópia que mais se assemelha a uma frase alvo, evoluindo gradualmente até alcançá-la.
""",
        'sidebar_header': "⚙️ Parâmetros da Simulação",
        'target_phrase_label': "Frase Alvo",
        'target_phrase_help': "Use apenas letras minúsculas (a-z), números (0-9) e espaços.",
        'mutation_rate_label': "Taxa de Mutação",
        'mutation_rate_help': "A probabilidade de cada caractere sofrer mutação. Taxas mais altas podem acelerar a convergência, mas também podem ser instáveis.",
        'population_size_label': "Tamanho da População",
        'population_size_help': "O número de 'descendentes' gerados em cada geração. Populações maiores exploram mais possibilidades.",
        'start_button': "▶️ Iniciar Simulação",
        'stop_button': "⏹️ Parar Simulação",
        'empty_target_error': "A frase alvo não pode estar vazia.",
        'invalid_target_error': "Frase alvo inválida. Use apenas [a-z0-9 ] caracteres.",
        'simulation_progress_header': "🚀 Progresso da Simulação",
        'generation_metric': "Geração",
        'score_metric': "Pontuação",
        'accuracy_metric': "Precisão",
        'progress_bar_text': "Progresso: {accuracy:.2f}%",
        'history_header': "📜 Histórico da Evolução",
        'history_entry': "Geração {generation}: {candidate}",
        'success_message': "🎉 Sucesso! A frase alvo foi alcançada na geração {generation}.",
        'stop_message': "Simulação parada pelo usuário.",
        'info_message': "Ajuste os parâmetros na barra lateral e clique em 'Iniciar Simulação' para começar.",
        'language_select': "Idioma / Language"
    },
    'en': {
        'page_title': "Dawkins’ Weasel Program",
        'main_title': "🧬 Dawkins’ Weasel Program",
        'description': """
This application demonstrates the "Weasel Program", a thought experiment by Richard Dawkins. 
The goal is to show how cumulative selection can generate complex results from randomness and selection.
Starting with a random phrase, the program generates copies with a small chance of mutation in each generation and selects the copy that most closely resembles a target phrase, gradually evolving until it reaches the target.
""",
        'sidebar_header': "⚙️ Simulation Parameters",
        'target_phrase_label': "Target Phrase",
        'target_phrase_help': "Use only lowercase letters (a-z), numbers (0-9), and spaces.",
        'mutation_rate_label': "Mutation Rate",
        'mutation_rate_help': "The probability of each character mutating. Higher rates can speed up convergence but may also be unstable.",
        'population_size_label': "Population Size",
        'population_size_help': "The number of 'offspring' generated in each generation. Larger populations explore more possibilities.",
        'start_button': "▶️ Start Simulation",
        'stop_button': "⏹️ Stop Simulation",
        'empty_target_error': "The target phrase cannot be empty.",
        'invalid_target_error': "Invalid target phrase. Use only [a-z0-9 ] characters.",
        'simulation_progress_header': "🚀 Simulation Progress",
        'generation_metric': "Generation",
        'score_metric': "Score",
        'accuracy_metric': "Accuracy",
        'progress_bar_text': "Progress: {accuracy:.2f}%",
        'history_header': "📜 Evolution History",
        'history_entry': "Generation {generation}: {candidate}",
        'success_message': "🎉 Success! The target phrase was reached in generation {generation}.",
        'stop_message': "Simulation stopped by user.",
        'info_message': "Adjust the parameters in the sidebar and click 'Start Simulation' to begin.",
        'language_select': "Language / Idioma"
    }
}
