# Overleaf and local latexmk: when aamas2027.tex needs aamas2027_supplement.aux
# (via xr-hyper \externaldocument), build the supplement first. The
# XR_NESTED guard stops the supplement build from recursing back into the
# main paper, which it also references.
add_cus_dep('tex', 'aux', 0, 'makeexternaldocument');
sub makeexternaldocument {
    return 0 if $ENV{'XR_NESTED'};
    if (!($root_filename eq $_[0])) {
        local $ENV{'XR_NESTED'} = 1;
        system("latexmk -cd -pdf -interaction=nonstopmode \"$_[0]\"");
    }
    return 0;
}
