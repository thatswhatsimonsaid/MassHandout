EXPERIMENT_CONFIG = {
    ### Mass booklet configurations ###
    "output_dir": "output",
    "dates": ["093026", "100126", "100226"],
    "default_inputs": {
        "hymns": {},
        "reading1": {"lang": "eng", "option_index": 0},
        "psalm":    {"lang": "viet", "option_index": 0},
        "reading2": {"lang": "eng", "option_index": 0},
        "alleluia": {"lang": "viet", "option_index": 0},
        "gospel":   {"lang": "eng", "option_index": 0}
    },

    ### HPC Configuration ###
    "slurm": {
        "partition": "short",
        "time": "0:05:00",
        "mem_per_cpu": "1G",
        "mail_type": "FAIL",
        "mail_user": "simon.nguyen1@veym.net"
    }
}