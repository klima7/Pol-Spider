{
    logdir: "logdir/pol_spider_mix_bert_run",
    model_config: "configs/spider/nl2code-bert.jsonnet",
    model_config_args: {
        data_path: 'data/pol_spider/',
        bs: 6,
        num_batch_accumulated: 4,
        bert_version: "bert-base-multilingual-uncased",
        summarize_header: "avg",
        use_column_type: false,
        max_steps: 81000,
        num_layers: 8,
        lr: 7.44e-4,
        bert_lr: 3e-6,
        att: 1,
        end_lr: 0,
        sc_link: true,
        cv_link: true,
        use_align_mat: true,
        use_align_loss: true,
        bert_token_type: true,
        decoder_hidden_size: 512,
        end_with_from: true, # equivalent to "SWGOIF" if true
        clause_order: null, # strings like "SWGOIF", it will be prioriotized over end_with_from 
    },

    eval_name: "bert_run_%s_%d" % [self.eval_use_heuristic, self.eval_beam_size],
    eval_output: "logdir/pol_spider_mix_evaluation/eval",
    eval_beam_size: 1,
    eval_use_heuristic: true,
    eval_steps: [32500],
    eval_section: "val",
}
