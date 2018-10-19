# language-learning/src/grammar_learner/pqa_table.py                    80928
# Test Grammar Learner to fill in ULL Project Plan Parses spreadshit
import os
import sys
import time
from .read_files import check_dir
from ..common import handle_path_string
from ..grammar_tester import test_grammar
from ..grammar_tester.optconst import *
from .learner import learn_grammar


def params(corpus, dataset, module_path, out_dir, **kwargs):
    input_parses = module_path + '/data/' + corpus + '/' + dataset
    if check_dir(input_parses, create=False, verbose='min'):
        batch_dir = out_dir + '/' + corpus
        spaces = ['w', 'c', 'd']    # 'words','connectors', 'disjuncts'
        context = spaces[kwargs['context']]
        rules = spaces[kwargs['grammar_rules']]
        if kwargs['grammar_rules'] == -1:
            rules = 'interconnected'
        elif kwargs['grammar_rules'] == -2:
            rules = 'linked'
        if kwargs['clustering'] == 'random':
            context = ''
            wtf = 'Random-clusters'
        elif kwargs['word_space'] == 'vectors':
            wtf = 'DRK'
        else: wtf = 'ILE'
        if kwargs['left_wall'] in ['','none']:
            left_wall = 'no-LW' #'no-LEFT-WALL'
        else: left_wall = 'LW'  # 'LEFT-WALL'
        if kwargs['period']:
            period = 'period'
        else: period = 'no-period'
        # generalization = ['no-generalization', 'generalized-categories', \
        #                   'generalized-rules', 'generalized-categories-and-rules']
        generalization = ['no-gen', 'gen-cats', 'gen-rules', 'gen-both']
        gen = 0
        if 'categories_generalization' in kwargs:
            if kwargs['categories_generalization'] not in ['','off','none']: gen += 1
        if 'rules_generalization' in kwargs:
            if kwargs['rules_generalization'] not in ['','off','none']:  gen += 2
        #-prj_dir = batch_dir + '_' + dataset  + '_' + \
        #-    spaces[kwargs['context']] + '-'+wtf+'-' + spaces[kwargs['grammar_rules']] \
        #-    + '_' + left_wall + '_' + period + '_' + generalization[gen]
        # 80827 Shorter directories  #FIXME: restore long?
        # prj_dir = batch_dir +'_'+ dataset  +'_'+ context +'-'+ wtf +'-'+ rules
        # 80929:
        prj_dir = batch_dir + '_' + dataset  + '_' + context + wtf + rules \
            + '_' + left_wall + '_' + period + '_' + generalization[gen]

        if check_dir(prj_dir, create=True, verbose='none'):
            output_categories = prj_dir     # no file name ⇒ auto file name
            output_grammar = prj_dir        # no file name ⇒ auto file name
            return input_parses, output_categories, output_grammar
        else: return input_parses, out_dir, out_dir
    else: raise FileNotFoundError('File not found', input_parses)


def pqa_meter(dict_path, output_path, corpus_path, reference_path, runs=(1,1), **kwargs):
    #-output_path   = output_grammar
    #-dict_path     = input_path
    grammar_path  = output_path
    template_path = handle_path_string("tests/test-data/dict/poc-turtle")
    linkage_limit = kwargs['linkage_limit'] #100
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    #80719 added BIT_ULL_IN for table_cds - Child Directed Speech
    #80719: BIT_CAPS = preserve caps
    # pa, pq, pqa = test_grammar(corpus_path, output_path, dict_path, \
    #     grammar_path, template_path, linkage_limit, options, reference_path)
    pa, f1, pr, rc = test_grammar(corpus_path, output_path, dict_path, \
        grammar_path, template_path, linkage_limit, options, reference_path)
    return pa, rc, f1


def table_damb(lines, out_dir, cps=(0,0), rps=(0,0), runs=(1,1), **kwargs):
    #80720: table_amb 2.0: module_path, corpus_path, test_path built-in
    # cps,rps: tuples len=2 corpus_paths, reference_paths for Amb and disAmb corpora
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    rpd = module_path + '/data/POC-English-Amb/MST-fixed-manually/poc-english_ex-parses-gold.txt'

    spaces = ''
    if kwargs['context'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    if kwargs['word_space'] == 'vectors':
        spaces += 'DRK'
    else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    else: spaces += 'd'

    details = []
    average = []

    for i,line in enumerate(lines):
        corpus = line[1]
        if corpus == 'POC-English-disAmb':
            if cps[1] == 0:
                cp = rpd  # default reference_path
            else: cp = cps[1]
            if rps[1] == 0:
                rp = rpd
            else: rp = rps[1]
        else:
            if cps[0] == 0:
                cp = rpd
            else: cp = cps[0]
            if rps[0] == 0:
                rp = rpd
            else: rp = rps[0]

        dataset = line[2]

        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' + '
        else:
            kwargs['period'] = False
            dot = ' -- '

        gen = line[5]  # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen not in ['none','off']: continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip,oc,og :: input_path, output_categories, output_grammar
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            re = learn_grammar(ip, oc, og, **kwargs)
            for i in range(runs[1]):
                a, q, qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                pa.append(a)
                pq.append(q)
                rules.append(re['grammar_rules'])
                rulestr = ' ' + str(re['grammar_rules']) + ' '
                line = [line[0], corpus, dataset, lw, dot, gen, spaces, rulestr, \
                        str(int(round(a,0)))+'%', str(int(round(q,0)))+'%']
                details.append(line)
        paa = int(round(sum(pa)/len(pa), 0))
        pqa = int(round(sum(pq)/len(pq), 0))
        rules_avg = int(round(sum(rules)/len(rules), 0))
        avg = [line[0], corpus, dataset, lw, dot, gen, spaces, rules_avg, \
               str(paa)+'%', str(pqa)+'%']
        average.append(avg)
    return average, details


def table_cds(lines, out_dir, cp, rp, runs=(1,1), **kwargs):            #80825
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    spaces = ''
    if kwargs['clustering'] == 'random':   #80825 Random clusters
        spaces += 'RND'
    else:
        if kwargs['context'] == 1:
            spaces += 'c'
        else: spaces += 'd'
        if kwargs['word_space'] == 'vectors':
            spaces += 'DRK'
        else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    elif kwargs['grammar_rules'] == -1:  #80825 interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2:  #80825 interconnected disjunct-style
        spaces += 'id'
    else: spaces += 'd'
    details = []
    average = []
    for i,line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' + '
        else:
            kwargs['period'] = False
            dot = ' -- '
        gen = line[5]  # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            try:
                re = learn_grammar(ip, oc, og, **kwargs)
                for i in range(runs[1]):
                    a, q, qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    rules.append(re['grammar_rules'])
                    rulestr = ' ' + str(re['grammar_rules']) + ' '
                    dline = [line[0], corpus, dataset, lw, dot, gen, spaces, rulestr, \
                        str(int(round(a,0)))+'%', str(int(round(q,0)))+'%']
                    details.append(dline)
            except:
                print('pqa_table.py table_cds: learn_grammar(ip,oc,og,**kwargs)', \
                      '⇒ exception:\n', sys.exc_info())
                pa.append(0)
                pq.append(0)
                rules.append(0)
                det_line = [line[0], corpus, dataset, lw, dot, gen, spaces, ' fail ','---','---']
                details.append(det_line)

        if len(pa) > 0:
            paa = int(round(sum(pa)/len(pa), 0))
            pqa = int(round(sum(pq)/len(pq), 0))
            non_zero_rules = [x for x in rules if x > 0]
            if len(non_zero_rules) > 0:
                average_rules_n = int(round(sum(non_zero_rules)/len(non_zero_rules), 0))
            else: average_rules_n = 0
            avg_line = [line[0], corpus, dataset, lw, dot, gen, spaces, \
                average_rules_n, str(paa)+'%', str(pqa)+'%']
            average.append(avg_line)

    return average, details


def table_no_pqa(lines, out_dir, cp, rp, runs=(1,1), **kwargs):
    # cp,rp: corpus_path, reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    spaces = ''
    if kwargs['context'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    if kwargs['word_space'] == 'vectors':
        spaces += 'DRK'
    else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    details = []
    average = []
    for i,line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' + '
        else:
            kwargs['period'] = False
            dot = ' -- '
        gen = line[5]  # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            try:
                re = learn_grammar(ip, oc, og, **kwargs)
                rules.append(re['grammar_rules'])
                rulestr = ' ' + str(re['grammar_rules']) + ' '
            except:
                print('pqa_table.py table_no_pqa: learn_grammar(ip,oc,og,**kwargs)', \
                      '⇒ exception:\n', sys.exc_info())
                rules.append(0)
                rulestr = 'fail'
            details.append([line[0], corpus, dataset, lw, dot, gen, spaces, \
                           rulestr, '---', '--'])
        non_zero_rules = [x for x in rules if x > 0]
        if len(non_zero_rules) > 0:
            average_rules_n = str(int(round(sum(non_zero_rules)/len(non_zero_rules), 0)))
        else: average_rules_n = 'fail'
        average.append([line[0], corpus, dataset, lw, dot, gen, spaces, \
            average_rules_n, '---', '---'])

    return average, details


def table_row(lines, out_dir, cp, rp, runs=(1,1), **kwargs):            #80928
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    spaces = ''
    if kwargs['clustering'] == 'random':    # 80825 Random clusters
        spaces += 'RND'
    else:
        if kwargs['context'] == 1:
            spaces += 'c'
        else: spaces += 'd'
        if kwargs['word_space'] == 'vectors':
            spaces += 'DRK'
        else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    elif kwargs['grammar_rules'] == -1: # 80825 interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2: # 80825 interconnected disjunct-style
        spaces += 'id'
    else: spaces += 'd'
    details = []
    average = []
    for i,line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' . '
        else:
            kwargs['period'] = False
            dot = ' -- '
        gen = line[5]   # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''
        pa = []
        pq = []
        si = []     # Silhouiette index
        rules = []
        for j in range(runs[0]):
            if True: #try:      # try - except hides errors?  FIXME
                #re = learn_grammar(ip, oc, og, **kwargs)
                re = learn_grammar(**kwargs)
                if 'silhouette' in re:
                    s = round(re['silhouette'], 2)
                    s_str = str(s)
                else:
                    s = 0
                    s_str = ' --- '
                for i in range(runs[1]):
                    a, q, qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    si.append(s)
                    rules.append(re['grammar_rules'])
                    dline = [line[0], corpus, dataset, lw, dot, gen, spaces,
                        ' ' + str(re['grammar_rules']) + ' ', s_str,
                        str(int(round(a,0)))+'%', str(int(round(q,0)))+'%']
                    details.append(dline)
            else: #except:      # FIXME
                print('pqa_table.py table_cds: learn_grammar(**kwargs)',
                      '⇒ exception:\n', sys.exc_info())
                pa.append(0)
                pq.append(0)
                rules.append(0)
                det_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
                            ' fail ',' --- ',' --- ',' --- ']
                details.append(det_line)
                #continue
        if len(pa) > 0:
            paa = int(round(sum(pa) / len(pa), 0))
            pqa = int(round(sum(pq) / len(pq), 0))
            sia = round(sum(si) / len(si), 2)
            sia_str = str(sia) if sia > 0.005 else '---'
            non_zero_rules = [x for x in rules if x > 0]
            if len(non_zero_rules) > 0:
                average_rules_n = int(round(sum(non_zero_rules)/len(non_zero_rules), 0))
            else: average_rules_n = 0
            avg_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
                average_rules_n, sia_str, str(paa)+'%', str(pqa)+'%']
            average.append(avg_line)

    return average, details


#Notes:

#80802 /src/poc05.py restructured, def params moved here, further dev here
    #legacy pqa_table.py renamed pqa05.py ~ poc05+pqa05=baseline (DEL later)
#80825 kwargs['grammar_rules'] == -1,-2: interconnected clusters
    #-1: connectors #Cxx: {C01Cxx- or ... CnCxx-} and {CxxC01+ or ... CxxCn+}
    #-2: disjuncts  #Cxx: (C01Cxx-) or (C02Cxx-) ... or (CxxCn+)
#TODO: replace table_damb, table_cds ⇒ table_row with silhouette & new metrics
