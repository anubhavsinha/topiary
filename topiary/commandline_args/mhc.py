
# Copyright (c) 2016. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Commandline options for MHC Binding Prediction
"""

from __future__ import print_function, division, absolute_import
import logging

from mhcnames import normalize_allele_name
import mhctools

from ..parsing_helpers import parse_int_list

mhc_predictors = {
    "netmhc": mhctools.NetMHC,
    "netmhcpan": mhctools.NetMHCpan,
    "netmhciipan": mhctools.NetMHCIIpan,
    "netmhccons": mhctools.NetMHCcons,
    "random": mhctools.RandomBindingPredictor,
    # TODO implement SMM predictors in mhctools
    "smm": None,
    "smm-pmbec": None,
    # use NetMHCpan via IEDB's web API
    "netmhcpan-iedb": mhctools.IedbNetMHCpan,
    # use NetMHCcons via IEDB's web API
    "netmhccons-iedb": mhctools.IedbNetMHCcons,
    # use SMM via IEDB's web API
    "smm-iedb": mhctools.IedbSMM,
    # use SMM-PMBEC via IEDB's web API
    "smm-pmbec-iedb": mhctools.IedbSMM_PMBEC,
    # Class II MHC binding prediction using NetMHCIIpan via IEDB
    "netmhciipan-iedb": mhctools.IedbNetMHCIIpan,
}

def add_mhc_args(arg_parser):
    mhc_options_arg_group = arg_parser.add_argument_group(
        title="MHC Prediction Options",
        description="MHC Binding Prediction Options")

    mhc_options_arg_group.add_argument(
        "--mhc-predictor",
        choices=list(sorted(mhc_predictors.keys())),
        type=lambda s: s.lower().strip(),
        required=True)

    mhc_options_arg_group.add_argument(
        "--mhc-epitope-lengths",
        default=[8, 9, 10, 11],
        type=parse_int_list,
        help="Lengths of epitopes to consider for MHC binding prediction")

    mhc_options_arg_group.add_argument(
        "--mhc-alleles-file",
        help="File with one HLA allele per line")

    mhc_options_arg_group.add_argument(
        "--mhc-alleles",
        default="",
        help="Comma separated list of allele (default HLA-A*02:01)")

    return mhc_options_arg_group

def mhc_alleles_from_args(args):
    alleles = [
        normalize_allele_name(allele.strip())
        for allele in args.mhc_alleles.split(",")
        if allele.strip()
    ]
    if args.mhc_alleles_file:
        with open(args.mhc_alleles_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    alleles.append(normalize_allele_name(line))
    if len(alleles) == 0:
        raise ValueError(
            "MHC alleles required (use --mhc-alleles or --mhc-alleles-file)")
    return alleles


def mhc_binding_predictor_from_args(args):
    mhc_class = mhc_predictors.get(args.mhc_predictor)
    if mhc_class is None:
        raise ValueError(
            "Invalid MHC prediction method: %s" % (args.mhc_predictor,))
    alleles = mhc_alleles_from_args(args)
    epitope_lengths = args.mhc_epitope_lengths
    logging.info(
        ("Building MHC binding prediction %s"
         " for alleles %s"
         " and epitope lengths %s") % (
            mhc_class.__class__.__name__,
            alleles,
            epitope_lengths))
    return mhc_class(
        alleles=alleles,
        epitope_lengths=epitope_lengths)
