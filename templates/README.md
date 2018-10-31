# IBA Probes

The files in this folder are IBA probe json payloads that are represented as
[JINJA templates](http://jinja.pocoo.org/docs/2.10/templates/). You need to use
aos-cli to load these probes on to AOS server. The command to use in aos-cli is
`probe create --blueprint <id> --file </path/to/template/file> [<additional_args>]`
