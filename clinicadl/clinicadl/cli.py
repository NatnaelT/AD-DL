# coding: utf8

import argparse

from clinicadl.tools.deep_learning.iotools import Parameters
from colorama import Fore


TRAIN_CATEGORIES = {
    # General parent group
    'POSITIONAL': '%sPositional arguments%s' % (Fore.BLUE, Fore.RESET),
    'COMPUTATIONAL': '%sComputational issues%s' % (Fore.BLUE, Fore.RESET),
    'DATA': '%sData management%s' % (Fore.BLUE, Fore.RESET),
    'CROSS-VALIDATION': '%sCross-validation arguments%s' % (Fore.BLUE, Fore.RESET),
    'OPTIMIZATION': '%sOptimization parameters%s' % (Fore.BLUE, Fore.RESET),
    # Other parent groups
    'TRANSFER LEARNING': '%sTransfer learning%s' % (Fore.BLUE, Fore.RESET),
    'AUTOENCODER': '%sAutoencoder specific%s' % (Fore.BLUE, Fore.RESET),
    # Image-level
    'IMAGE OPTIMIZATION': '%sImage-level optimization parameters%s' % (Fore.BLUE, Fore.RESET),
    'IMAGE DATA MANAGEMENT': '%sImage-level data management%s' % (Fore.BLUE, Fore.RESET),
    # Slice-level
    'SLICE': '%sSlice-level parameters%s' % (Fore.BLUE, Fore.RESET),
    # Patch arguments
    'PATCH': '%sPatch-level parameters%s' % (Fore.BLUE, Fore.RESET),
    'PATCH CNN': '%sPatch-level CNN parameters%s' % (Fore.BLUE, Fore.RESET),
    # ROI-based arguments
    'ROI': '%sROI-based parameters%s' % (Fore.BLUE, Fore.RESET),
    'ROI CNN': '%sROI-based CNN parameters%s' % (Fore.BLUE, Fore.RESET),
}


def set_default_dropout(args):
    if args.dropout is None:
        if args.mode == 'image':
            args.dropout = 0.5
        elif args.mode == 'slice':
            args.dropout = 0.8
        else:
            args.dropout = 0


def preprocessing_t1w_func(args):
    from .preprocessing.T1_linear import preprocessing_t1w
    wf = preprocessing_t1w(
            args.bids_dir,
            args.caps_dir,
            args.tsv_file,
            args.working_dir
            )
    wf.run(plugin='MultiProc', plugin_args={'n_procs': args.nproc})


def extract_data_func(args):
    from .preprocessing.T1_preparedl import extract_dl_t1w

    wf = extract_dl_t1w(
            args.caps_dir,
            args.tsv_file,
            args.working_dir,
            args.extract_method,
            args.patch_size,
            args.stride_size,
            args.slice_direction,
            args.slice_mode
            )
    wf.run(plugin='MultiProc', plugin_args={'n_procs': args.nproc})


def generate_data_func(args):
    from .tools.data.generate_data import generate_random_dataset, generate_trivial_dataset

    if args.mode == "random":
        generate_random_dataset(
            caps_dir=args.caps_dir,
            tsv_path=args.tsv_path,
            output_dir=args.output_dir,
            n_subjects=args.n_subjects,
            mean=args.mean,
            sigma=args.sigma,
            preprocessing=args.preprocessing,
            output_size=args.output_size)
    else:
        generate_trivial_dataset(
            caps_dir=args.caps_dir,
            tsv_path=args.tsv_path,
            output_dir=args.output_dir,
            n_subjects=args.n_subjects,
            preprocessing=args.preprocessing,
            output_size=args.output_size,
            mask_path=args.mask_path,
            atrophy_percent=args.atrophy_percent,
            group=args.group
        )


# Function to dispatch training to corresponding function
def train_func(args):
    from .subject_level.train_autoencoder import train_autoencoder
    from .subject_level.train_CNN import train_cnn
    from .slice_level.train_CNN import train_slice
    from .patch_level.train_autoencoder import train_autoencoder_patch
    from .patch_level.train_singleCNN import train_patch_single_cnn
    from .patch_level.train_multiCNN import train_patch_multi_cnn

    set_default_dropout(args)
    print("Enter train_func")

    if args.mode == 'image':
        if args.mode_task == "autoencoder":
            train_params_autoencoder = Parameters(
                args.tsv_path,
                args.output_dir,
                args.caps_dir,
                args.network
            )
            train_params_autoencoder.write(
                transfer_learning_difference=args.transfer_learning_difference,
                preprocessing=args.preprocessing,
                diagnoses=args.diagnoses,
                baseline=args.baseline,
                minmaxnormalization=not args.unnormalize,
                n_splits=args.n_splits,
                split=args.split,
                accumulation_steps=args.accumulation_steps,
                epochs=args.epochs,
                learning_rate=args.learning_rate,
                patience=args.patience,
                tolerance=args.tolerance,
                add_sigmoid=args.add_sigmoid,
                optimizer='Adam',
                weight_decay=args.weight_decay,
                gpu=args.use_gpu,
                batch_size=args.batch_size,
                evaluation_steps=args.evaluation_steps,
                num_workers=args.nproc,
                visualization=args.visualization
            )
            train_autoencoder(train_params_autoencoder)
        else:
            train_params_cnn = Parameters(
                    args.tsv_path,
                    args.output_dir,
                    args.caps_dir,
                    args.network
            )
            train_params_cnn.write(
                    preprocessing=args.preprocessing,
                    diagnoses=args.diagnoses,
                    baseline=args.baseline,
                    minmaxnormalization=not args.unnormalize,
                    n_splits=args.n_splits,
                    split=args.split,
                    accumulation_steps=args.accumulation_steps,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    patience=args.patience,
                    tolerance=args.tolerance,
                    optimizer='Adam',
                    weight_decay=args.weight_decay,
                    dropout=args.dropout,
                    gpu=args.use_gpu,
                    batch_size=args.batch_size,
                    evaluation_steps=args.evaluation_steps,
                    num_workers=args.nproc,
                    transfer_learning_path=args.transfer_learning_path,
                    transfer_learning_autoencoder=args.transfer_learning_autoencoder,
                    selection=args.selection
            )
            train_cnn(train_params_cnn)
    elif args.mode == 'slice':
        train_params_slice = Parameters(
            args.tsv_path,
            args.output_dir,
            args.caps_dir,
            args.network
        )
        train_params_slice.write(
            mri_plane=args.slice_direction,
            diagnoses=args.diagnoses,
            baseline=args.baseline,
            learning_rate=args.learning_rate,
            patience=args.patience,
            tolerance=args.tolerance,
            n_splits=args.n_splits,
            split=args.split,
            epochs=args.epochs,
            batch_size=args.batch_size,
            optimizer='Adam',
            weight_decay=args.weight_decay,
            dropout=args.dropout,
            gpu=args.use_gpu,
            num_workers=args.nproc,
            selection_threshold=args.selection_threshold,
            prepare_dl=args.prepare_dl
        )
        train_slice(train_params_slice)
    elif args.mode == 'patch':
        if args.mode_task == "autoencoder":
            train_params_autoencoder = Parameters(
                    args.tsv_path,
                    args.output_dir,
                    args.caps_dir,
                    args.network
                    )
            train_params_autoencoder.write(
                    diagnoses=args.diagnoses,
                    baseline=args.baseline,
                    n_splits=args.n_splits,
                    split=args.split,
                    accumulation_steps=args.accumulation_steps,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    patience=args.patience,
                    tolerance=args.tolerance,
                    add_sigmoid=args.add_sigmoid,
                    optimizer='Adam',
                    weight_decay=args.weight_decay,
                    gpu=args.use_gpu,
                    batch_size=args.batch_size,
                    evaluation_steps=args.evaluation_steps,
                    num_workers=args.nproc,
                    patch_size=args.patch_size,
                    patch_stride=args.patch_stride,
                    hippocampus_roi=False,
                    visualization=args.visualization,
                    prepare_dl=args.prepare_dl
                    )
            train_autoencoder_patch(train_params_autoencoder)
        else:
            train_params_patch = Parameters(
                    args.tsv_path,
                    args.output_dir,
                    args.caps_dir,
                    args.network
                    )
            train_params_patch.write(
                    diagnoses=args.diagnoses,
                    baseline=args.baseline,
                    n_splits=args.n_splits,
                    split=args.split,
                    accumulation_steps=args.accumulation_steps,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    patience=args.patience,
                    tolerance=args.tolerance,
                    optimizer='Adam',
                    weight_decay=args.weight_decay,
                    dropout=args.dropout,
                    gpu=args.use_gpu,
                    batch_size=args.batch_size,
                    evaluation_steps=args.evaluation_steps,
                    num_workers=args.nproc,
                    transfer_learning_path=args.transfer_learning_path,
                    transfer_learning_autoencoder=args.transfer_learning_autoencoder,
                    transfer_learning_multicnn=args.transfer_learning_multicnn,
                    selection=args.selection,
                    patch_size=args.patch_size,
                    patch_stride=args.patch_stride,
                    hippocampus_roi=False,
                    selection_threshold=args.selection_threshold,
                    num_cnn=args.num_cnn,
                    prepare_dl=args.prepare_dl
                    )
            if args.network_type == 'single':
                train_patch_single_cnn(train_params_patch)
            else:
                train_patch_multi_cnn(train_params_patch)
    elif args.mode == 'roi':
        if args.mode_task == "autoencoder":
            train_params_autoencoder = Parameters(
                    args.tsv_path,
                    args.output_dir,
                    args.caps_dir,
                    args.network
                    )
            train_params_autoencoder.write(
                    diagnoses=args.diagnoses,
                    baseline=args.baseline,
                    n_splits=args.n_splits,
                    split=args.split,
                    accumulation_steps=args.accumulation_steps,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    patience=args.patience,
                    tolerance=args.tolerance,
                    add_sigmoid=args.add_sigmoid,
                    optimizer='Adam',
                    weight_decay=args.weight_decay,
                    gpu=args.use_gpu,
                    batch_size=args.batch_size,
                    evaluation_steps=args.evaluation_steps,
                    num_workers=args.nproc,
                    patch_size=args.patch_size,
                    patch_stride=args.patch_stride,
                    hippocampus_roi=True,
                    visualization=args.visualization,
                    prepare_dl=args.prepare_dl
                    )
            train_autoencoder_patch(train_params_autoencoder)
        else:
            train_params_patch = Parameters(
                    args.tsv_path,
                    args.output_dir,
                    args.caps_dir,
                    args.network
                    )
            train_params_patch.write(
                    diagnoses=args.diagnoses,
                    baseline=args.baseline,
                    n_splits=args.n_splits,
                    split=args.split,
                    accumulation_steps=args.accumulation_steps,
                    epochs=args.epochs,
                    learning_rate=args.learning_rate,
                    patience=args.patience,
                    tolerance=args.tolerance,
                    optimizer='Adam',
                    weight_decay=args.weight_decay,
                    dropout=args.dropout,
                    gpu=args.use_gpu,
                    batch_size=args.batch_size,
                    evaluation_steps=args.evaluation_steps,
                    num_workers=args.nproc,
                    transfer_learning_path=args.transfer_learning_path,
                    transfer_learning_autoencoder=args.transfer_learning_autoencoder,
                    transfer_learning_multicnn=args.transfer_learning_multicnn,
                    selection=args.selection,
                    patch_size=args.patch_size,
                    patch_stride=args.patch_stride,
                    hippocampus_roi=True,
                    selection_threshold=args.selection_threshold,
                    num_cnn=args.num_cnn,
                    prepare_dl=args.prepare_dl
                    )
            train_patch_single_cnn(train_params_patch)

    elif args.mode == 'svm':
        raise NotImplementedError("The SVM commandline was not implement yet.")
    else:
        print('Mode not detected in clinicadl')

# Function to dispatch command line options from classify to corresponding
# function


def classify_func(args):
    from .classify.inference import inference_from_model

    inference_from_model(
            args.caps_dir,
            args.tsv_file,
            args.output_dir,
            args.model_name,
            )


# Functions to dispatch command line options from tsvtool to corresponding function

def tsv_restrict_func(args):
    from .tools.tsv.restriction import aibl_restriction, oasis_restriction

    if args.dataset == "AIBL":
        aibl_restriction(args.merged_tsv, args.results_path)
    elif args.dataset == "OASIS":
        oasis_restriction(args.merged_tsv, args.results_path)


def tsv_getlabels_func(args):
    from .tools.tsv.data_formatting import get_labels

    get_labels(
        args.merged_tsv,
        args.missing_mods,
        args.results_path,
        diagnoses=args.diagnoses,
        modality=args.modality,
        restriction_path=args.restriction_path,
        time_horizon=args.time_horizon)


def tsv_split_func(args):
    from .tools.tsv.data_split import split_diagnoses

    split_diagnoses(
        args.merged_tsv,
        args.formatted_data_path,
        n_test=args.n_test,
        subset_name=args.subset_name,
        age_name=args.age_name,
        MCI_sub_categories=args.MCI_sub_categories,
        t_val_threshold=args.t_val_threshold,
        p_val_threshold=args.p_val_threshold)


def tsv_kfold_func(args):
    from .tools.tsv.kfold_split import split_diagnoses

    split_diagnoses(
        args.formatted_data_path,
        n_splits=args.n_splits,
        subset_name=args.subset_name,
        MCI_sub_categories=args.MCI_sub_categories)


def tsv_analysis_func(args):
    from .tools.tsv.demographics_analysis import demographics_analysis

    demographics_analysis(
        args.merged_tsv,
        args.formatted_data_path,
        args.results_path,
        diagnoses=args.diagnoses,
        mmse_name=args.mmse_name,
        age_name=args.age_name,
        baseline=args.baseline)


def parse_command_line():
    parser = argparse.ArgumentParser(
            prog='clinicadl',
            description='Clinica Deep Learning.')

    parser.add_argument('--verbose', '-v', action='count')

    subparser = parser.add_subparsers(
            title='''Task to execute with clinicadl:''',
            description='''What kind of task do you want to use with clinicadl?
            (tsvtool, preprocessing, extract, generate, train, validate, classify).''',
            dest='task',
            help='''****** Tasks proposed by clinicadl ******''')

    subparser.required = True

    # Generate synthetic data
    generate_parser = subparser.add_parser(
            'generate',
            help='Generate synthetic data for functional tests.'
            )
    generate_parser.add_argument(
            'mode',
            help='Choose which dataset is generated (random, trivial).',
            choices=['random', 'trivial'],
            default='random'
            )
    generate_parser.add_argument(
            'caps_dir',
            help='Data using CAPS structure.',
            default=None
            )
    generate_parser.add_argument(
            'tsv_path',
            help='TSV path with subjects/sessions to use for data generation.',
            default=None
            )
    generate_parser.add_argument(
            'output_dir',
            help='Folder containing the synthetic dataset.',
            default=None
            )
    generate_parser.add_argument(
            '--n_subjects',
            type=int,
            default=300,
            help="Number of subjects in each class of the synthetic dataset."
            )
    generate_parser.add_argument(
            '--preprocessing',
            type=str,
            default='t1-linear',
            choices=['t1-linear', 't1-volume'],
            help="Preprocessing used to generate synthetic data."
            )
    generate_parser.add_argument(
            '--output_size',
            type=int,
            nargs="+",
            default=None,
            help="If a value is given, interpolation will be used to up/downsample the image."
            )
    generate_parser.add_argument(
            '--mean',
            type=float,
            default=0,
            help="Mean value of the noise added for the random dataset."
            )
    generate_parser.add_argument(
            '--sigma',
            type=float,
            default=0.5,
            help="Standard deviation of the noise added for the random dataset."
            )
    generate_parser.add_argument(
            '--mask_path',
            type=str,
            help='path to the extracted masks to generate the two labels.',
            default=None
            )
    generate_parser.add_argument(
            '--atrophy_percent',
            type=float,
            default=60,
            help='percentage of atrophy applied'
            )
    generate_parser.add_argument(
            '--group',
            type=str,
            default=None,
            help="Specific argument for dartel preprocessing."
            )

    generate_parser.set_defaults(func=generate_data_func)

    # Preprocessing 1
    # preprocessing_parser: get command line arguments and options for
    # preprocessing

    preprocessing_parser = subparser.add_parser(
            'preprocessing',
            help='Prepare data for training (needs clinica installed).')
    preprocessing_parser.add_argument(
            'bids_dir',
            help='Data using BIDS structure.',
            default=None
            )
    preprocessing_parser.add_argument(
            'caps_dir',
            help='Data using CAPS structure.',
            default=None
            )
    preprocessing_parser.add_argument(
            'tsv_file',
            help='TSV file with subjects/sessions to process.',
            default=None
            )
    preprocessing_parser.add_argument(
            'working_dir',
            help='Working directory to save temporary file.',
            default=None
            )
    preprocessing_parser.add_argument(
            '-np', '--nproc',
            help='Number of cores used for processing (2 by default)',
            type=int, default=2
            )

    preprocessing_parser.set_defaults(func=preprocessing_t1w_func)

    # Preprocessing 2 - Extract data: slices or patches
    # extract_parser: get command line argument and options

    extract_parser = subparser.add_parser(
            'extract',
            help='Create data (slices or patches) for training.'
            )
    extract_parser.add_argument(
            'caps_dir',
            help='Data using CAPS structure.',
            default=None
            )
    extract_parser.add_argument(
            'tsv_file',
            help='TSV file with subjects/sessions to process.',
            default=None
            )
    extract_parser.add_argument(
            'working_dir',
            help='Working directory to save temporary file.',
            default=None
            )
    extract_parser.add_argument(
        'extract_method',
        help='''Method used to extract features. Three options:
             'slice' to get 2D slices from the MRI,
             'patch' to get 3D volumetric patches or
             'whole' to get the complete MRI.''',
        choices=['slice', 'patch', 'whole'], default='whole')
    extract_parser.add_argument(
        '-ps', '--patch_size',
        help='''Patch size (only for 'patch' extraction) e.g: --patch_size 50''',
        type=int, default=50)
    extract_parser.add_argument(
        '-ss', '--stride_size',
        help='''Stride size (only for 'patch' extraction) e.g.: --stride_size 50''',
        type=int, default=50)
    extract_parser.add_argument(
        '-sd', '--slice_direction',
        help='''Slice direction (only for 'slice' extraction). Three options:
             '0' -> Sagittal plane,
             '1' -> Coronal plane or
             '2' -> Axial plane''',
        type=int, default=0)
    extract_parser.add_argument(
        '-sm', '--slice_mode',
        help='''Slice mode (only for 'slice' extraction). Two options:
             'original' to save one single channel (intensity),
             'rgb' to saves three channel (with same intensity).''',
        choices=['original', 'rgb'], default='rgb')
    extract_parser.add_argument(
        '-np', '--nproc',
        help='Number of cores used for processing',
        type=int, default=2)

    extract_parser.set_defaults(func=extract_data_func)

    # Train - Train CNN model with preprocessed  data
    # train_parser: get command line arguments and options

    train_parser = subparser.add_parser(
            'train',
            help='Train with your data and create a model.')

    train_subparser = train_parser.add_subparsers(
        title='''Classifier to be trained''',
        description='''What classifier do you want to train?
                (image, slice, patch).''',
        dest='mode',
        help='''****** Tasks proposed by clinicadl ******''')

    train_subparser.required = True

    # Positional arguments
    train_parent_parser = argparse.ArgumentParser(add_help=False)
    train_pos_group = train_parent_parser.add_argument_group(TRAIN_CATEGORIES["POSITIONAL"])
    train_pos_group.add_argument(
        'caps_dir',
        help='Data using CAPS structure.',
        default=None)
    train_pos_group.add_argument(
        'tsv_path',
        help='TSV path with subjects/sessions to process.',
        default=None)
    train_pos_group.add_argument(
        'output_dir',
        help='Folder containing results of the training.',
        default=None)
    train_pos_group.add_argument(
        'network',
        help='CNN Model to be used during the training.',
        default='Conv5_FC3')

    # Computational issues
    train_comput_group = train_parent_parser.add_argument_group(TRAIN_CATEGORIES["COMPUTATIONAL"])
    train_comput_group.add_argument(
            '-gpu', '--use_gpu', action='store_true',
            help='Uses GPU instead of CPU if CUDA is available',
            default=False)
    train_comput_group.add_argument(
            '-np', '--nproc',
            help='Number of cores used during the training.',
            type=int, default=2)
    train_comput_group.add_argument(
            '--batch_size',
            default=2, type=int,
            help='Batch size for training. (default=2)')

    # Data management
    train_data_group = train_parent_parser.add_argument_group(TRAIN_CATEGORIES["DATA"])
    train_data_group.add_argument(
            '--diagnoses', '-d',
            help='Diagnoses that will be selected for training.',
            default=['AD', 'CN'], nargs='+', type=str, choices=['AD', 'CN', 'MCI', 'sMCI', 'pMCI'])
    train_data_group.add_argument(
            '--baseline',
            help='if True only the baseline is used.',
            action="store_true",
            default=False)

    # Cross-validation
    train_cv_group = train_parent_parser.add_argument_group(TRAIN_CATEGORIES["CROSS-VALIDATION"])
    train_cv_group.add_argument(
            '--n_splits',
            help='If a value is given will load data of a k-fold CV.',
            type=int, default=None)
    train_cv_group.add_argument(
            '--split',
            help='Will load the specific split wanted.',
            type=int, default=0)

    # Optimization parameters
    train_optim_group = train_parent_parser.add_argument_group(TRAIN_CATEGORIES["OPTIMIZATION"])
    train_optim_group.add_argument(
            '--epochs',
            help='Epochs through the data. (default=20)',
            default=20, type=int)
    train_optim_group.add_argument(
            '--learning_rate', '-lr',
            help='Learning rate of the optimization. (default=0.01)',
            default=1e-4, type=float)
    train_optim_group.add_argument(
            '--weight_decay', '-wd',
            help='Weight decay value used in optimization. (default=1e-4)',
            default=1e-4, type=float)
    train_optim_group.add_argument(
            '--dropout',
            help='rate of dropout that will be applied to dropout layers.',
            default=None, type=float)
    train_optim_group.add_argument(
            '--patience',
            help='Waiting time for early stopping.',
            type=int, default=10)
    train_optim_group.add_argument(
            '--tolerance',
            help='Tolerance value for the early stopping.',
            type=float, default=0.0)

    # Transfer learning
    transfer_learning_parent = argparse.ArgumentParser(add_help=False)
    transfer_learning_group = transfer_learning_parent.add_argument_group(TRAIN_CATEGORIES["TRANSFER LEARNING"])
    transfer_learning_group.add_argument(
            '--transfer_learning_path',
            help="If an existing path is given, a pretrained model is used.",
            type=str, default=None)
    transfer_learning_group.add_argument(
            '--transfer_learning_autoencoder',
            help='''If specified, do transfer learning using an autoencoder else will look
                 for a CNN model.''',
            default=False, action="store_true")

    # Autoencoder
    autoencoder_parent = argparse.ArgumentParser(add_help=False)
    autoencoder_group = autoencoder_parent.add_argument_group(TRAIN_CATEGORIES["AUTOENCODER"])
    autoencoder_group.add_argument(
        '--add_sigmoid',
        help='Add sigmoid function at the end of the decoder.',
        default=False, action="store_true")
    autoencoder_group.add_argument(
        '--visualization',
        help='Save results in visualization folder.',
        action="store_true",
        default=False)

    ######################
    # IMAGE
    ######################
    train_image_parser = train_subparser.add_parser(
        "image",
        help="Train a 3D-image level network.")

    train_image_parent = argparse.ArgumentParser(add_help=False)
    train_imageoptim_group = train_image_parent.add_argument_group(TRAIN_CATEGORIES["IMAGE OPTIMIZATION"])
    train_imageoptim_group.add_argument(
        '--evaluation_steps', '-esteps',
        default=0, type=int,
        help='Fix the number of batches to use before validation.')
    train_imageoptim_group.add_argument(
        '--accumulation_steps', '-asteps',
        help='Accumulates gradients in order to increase the size of the batch.',
        default=1, type=int)

    train_imagedata_group = train_image_parent.add_argument_group(TRAIN_CATEGORIES["IMAGE DATA MANAGEMENT"])
    train_imagedata_group.add_argument(
        '--preprocessing',
        help='Defines the type of preprocessing of CAPS data.',
        choices=['t1-linear', 't1-volume'], type=str,
        default='t1-linear')
    train_imagedata_group.add_argument(
        '--unnormalize', '-un',
        help='Disable default MinMaxNormalization.',
        action="store_true",
        default=False)

    train_image_subparser = train_image_parser.add_subparsers(
        title='''Task to be performed''',
        description='''Autoencoder or cnn?''',
        dest='mode_task',
        help='''****** Choose between autoencoder or CNN training ******''')

    train_image_ae_parser = train_image_subparser.add_parser(
        "autoencoder",
        parents=[train_parent_parser, train_image_parent, autoencoder_parent, transfer_learning_parent],
        help="Train a 3D-patch level autoencoder.")
    # /!\ If parents list is changed the arguments won't be in the right group anymore !
    train_image_ae_parser._action_groups[-1].add_argument(
        '--transfer_learning_difference',
        help='''Difference of size between the pretrained autoencoder and
        the training one. If the new one is larger, difference will be
        positive.''',
        type=int, default=0)

    train_image_ae_parser.set_defaults(func=train_func)

    train_image_cnn_parser = train_image_subparser.add_parser(
        "cnn",
        parents=[train_parent_parser, train_image_parent, transfer_learning_parent],
        help="Train a 3D-patch level CNN.")
    # /!\ If parents list is changed the arguments won't be in the right group anymore !
    train_image_cnn_parser._action_groups[-1].add_argument(
            '--selection',
            help="If transfer_learning from CNN, chooses which best transfer model is selected.",
            type=str, default="best_acc", choices=["best_loss", "best_acc"])

    train_image_cnn_parser.set_defaults(func=train_func)

    #########################
    # SLICE
    #########################
    train_slice_parser = train_subparser.add_parser(
        "slice",
        parents=[train_parent_parser],
        help="Train a 2D-slice level CNN.")

    train_slice_group = train_slice_parser.add_argument_group(TRAIN_CATEGORIES["SLICE"])
    train_slice_group.add_argument(
        '--slice_direction', '-sd',
        help='''Which coordinate axis to take for slicing the MRI.
             0 for sagittal
             1 for coronal
             2 for axial direction.''',
        default=0, type=int)
    train_slice_group.add_argument(
        '--prepare_dl',
        help='''If True the outputs of extract preprocessing are used, else the whole
             MRI is loaded.''',
        default=False, action="store_true")

    train_slice_parser.set_defaults(func=train_func)

    #########################
    # PATCH
    #########################
    train_patch_parser = train_subparser.add_parser(
        "patch",
        help="Train a 3D-patch level network.")

    train_patch_parent = argparse.ArgumentParser(add_help=False)
    train_patch_group = train_patch_parent.add_argument_group(TRAIN_CATEGORIES["PATCH"])
    train_patch_group.add_argument(
        '-ps', '--patch_size',
        help='Patch size',
        type=int, default=50)
    train_patch_group.add_argument(
        '-ss', '--stride_size',
        help='Stride size',
        type=int, default=50)
    train_patch_group.add_argument(
        '--prepare_dl',
        help='''If True the outputs of extract preprocessing are used, else the whole
             MRI is loaded.''',
        default=False, action="store_true")

    train_patch_subparser = train_patch_parser.add_subparsers(
        title='''Task to be performed''',
        description='''Autoencoder or cnn?''',
        dest='mode_task',
        help='''****** Choose between autoencoder or CNN training ******''')
    train_patch_subparser.required = True

    train_patch_ae_parser = train_patch_subparser.add_parser(
        "autoencoder",
        parents=[train_parent_parser, train_patch_parent, autoencoder_parent],
        help="Train a 3D-patch level autoencoder.")

    train_patch_ae_parser.set_defaults(func=train_func)

    train_patch_cnn_parser = train_patch_subparser.add_parser(
        "cnn",
        parents=[train_parent_parser, train_patch_parent, transfer_learning_parent],
        help="Train a 3D-patch level CNN.")
    # /!\ If parents list is changed the arguments won't be in the right group anymore !
    train_patch_cnn_parser._action_groups[-1].add_argument(
        '--selection',
        help="If transfer_learning from CNN, chooses which best transfer model is selected.",
        type=str, default="best_acc", choices=["best_loss", "best_acc"])
    train_patch_cnn_parser._action_groups[-1].add_argument(
        '--transfer_learning_multicnn',
        help='''Specify if the transfer learning is from multi-CNNs to multi-CNNs.''',
        default=False, action="store_true")

    train_patch_cnn_group = train_patch_cnn_parser.add_argument_group(TRAIN_CATEGORIES["PATCH CNN"])
    train_patch_cnn_group.add_argument(
        '--network_type',
        help='Chose between single or multi CNN.',
        choices=['single', 'multi'], type=str,
        default='single')
    train_patch_cnn_group.add_argument(
        '--num_cnn',
        help='''How many CNNs are trained in a patch-wise way.
        This argument is used only if network_type is 'multi'.''',
        default=36, type=int)
    train_patch_cnn_group.add_argument(
        '--selection_threshold',
        help='''Threshold on the balanced accuracies to compute the
             subject-level performance. Patches are selected if their balanced
             accuracy > threshold. Default corresponds to no selection.''',
        type=float, default=0.0)

    train_patch_cnn_parser.set_defaults(func=train_func)

    #########################
    # ROI
    #########################
    train_roi_parser = train_subparser.add_parser(
        "roi",
        help="Train a ROI-based level network.")

    train_roi_parent = argparse.ArgumentParser(add_help=False)
    train_roi_group = train_roi_parent.add_argument_group(TRAIN_CATEGORIES["ROI"])
    train_roi_group.add_argument(
        '--prepare_dl',
        help='''If True the outputs of extract preprocessing are used, else the whole
             MRI is loaded.''',
        default=False, action="store_true")

    train_roi_subparser = train_roi_parser.add_subparsers(
        title='''Task to be performed''',
        description='''Autoencoder or cnn?''',
        dest='mode_task',
        help='''****** Choose between autoencoder or CNN training ******''')
    train_roi_subparser.required = True

    train_roi_ae_parser = train_roi_subparser.add_parser(
        "autoencoder",
        parents=[train_parent_parser, train_roi_parent, autoencoder_parent],
        help="Train a 3D-patch level autoencoder.")

    train_roi_ae_parser.set_defaults(func=train_func)

    train_roi_cnn_parser = train_roi_subparser.add_parser(
        "cnn",
        parents=[train_parent_parser, train_roi_parent, transfer_learning_parent],
        help="Train a 3D-patch level CNN.")
    # /!\ If parents list is changed the arguments won't be in the right group anymore !
    train_roi_cnn_parser._action_groups[-1].add_argument(
        '--selection',
        help="If transfer_learning from CNN, chooses which best transfer model is selected.",
        type=str, default="best_acc", choices=["best_loss", "best_acc"])

    train_roi_cnn_group = train_roi_cnn_parser.add_argument_group(TRAIN_CATEGORIES["ROI CNN"])
    train_roi_cnn_group.add_argument(
        '--selection_threshold',
        help='''Threshold on the balanced accuracies to compute the
             subject-level performance. ROIs are selected if their balanced
             accuracy > threshold. Default corresponds to no selection.''',
        type=float, default=0.0)

    train_roi_cnn_group.set_defaults(func=train_func)

    #########################
    # SVM
    #########################
    # train_svm_parser = train_subparser.add_parser(
    #     "svm",
    #     parents=[train_parent_parser],
    #     help="Train a SVM.")
    #
    # train_svm_parser.set_defaults(func=train_func)

    # Classify - Classify a subject or a list of tsv files with the CNN
    # provided as argument.
    # classify_parser: get command line arguments and options

    classify_parser = subparser.add_parser(
            'classify',
            help='''Classify one image or a list of images with your previously
                 trained model.''')
    classify_parser.add_argument(
            'caps_dir',
            help='Data using CAPS structure.',
            default=None)
    classify_parser.add_argument(
            'tsv_path',
            help='TSV path with subjects/sessions to process.',
            default=None)
    classify_parser.add_argument(
            'output_dir',
            help='Folder containing results of the training.',
            default=None)
    classify_parser.add_argument(
            'model_name',
            help='Model used for classification.',
            choices=['2D_slice', '3D_patch_1', '3D_patch_2', 'subject_1', 'subject_2'],
            default='2D_slice')

    classify_parser.set_defaults(func=classify_func)

    tsv_parser = subparser.add_parser(
        'tsvtool',
        help='''Handle tsv files for metadata processing and data splits''')

    tsv_subparser = tsv_parser.add_subparsers(
        title='''Task to execute with tsv tool:''',
        description='''What kind of task do you want to use with tsv tool?
                (restrict, getlabels, split, kfold, analysis).''',
        dest='tsv_task',
        help='''****** Tasks proposed by clinicadl tsv tool ******''')

    tsv_subparser.required = True

    tsv_restrict_subparser = tsv_subparser.add_parser(
        'restrict',
        help='Reproduce restrictions applied to AIBL and OASIS datasets')

    tsv_restrict_subparser.add_argument(
        "dataset",
        help="dataset on which the restriction is performed.",
        choices=["AIBL", "OASIS"],
        type=str)

    tsv_restrict_subparser.add_argument(
        "merged_tsv",
        help="Path to the file obtained by the command clinica iotools merge-tsv.",
        type=str)
    tsv_restrict_subparser.add_argument(
        "results_path",
        help="Path to the output tsv file (filename included).",
        type=str)

    tsv_restrict_subparser.set_defaults(func=tsv_restrict_func)

    tsv_getlabels_subparser = tsv_subparser.add_parser(
        'getlabels',
        help='Get labels in separate tsv files.')

    tsv_getlabels_subparser.add_argument(
        "merged_tsv",
        help="Path to the file obtained by the command clinica iotools merge-tsv.",
        type=str)
    tsv_getlabels_subparser.add_argument(
        "missing_mods",
        help="Path to the folder where the outputs of clinica iotools missing-mods are.",
        type=str)
    tsv_getlabels_subparser.add_argument(
        "results_path",
        type=str,
        help="Path to the folder where tsv files are extracted.")

    # Optional arguments
    tsv_getlabels_subparser.add_argument(
        "--modality", "-mod",
        help="Modality to select sessions. Sessions which do not include the modality will be excluded.",
        default="t1w", type=str)
    tsv_getlabels_subparser.add_argument(
        "--diagnoses",
        help="Labels that must be extracted from merged_tsv.",
        nargs="+", type=str, choices=['AD', 'CN', 'MCI', 'sMCI', 'pMCI'], default=['AD', 'CN'])
    tsv_getlabels_subparser.add_argument(
        "--time_horizon",
        help="Time horizon to analyse stability of MCI subjects.",
        default=36, type=int)
    tsv_getlabels_subparser.add_argument(
        "--restriction_path",
        help="Path to a tsv containing the sessions that can be included.",
        type=str, default=None)

    tsv_getlabels_subparser.set_defaults(func=tsv_getlabels_func)

    tsv_split_subparser = tsv_subparser.add_parser(
        'split',
        help='Performs one stratified shuffle split on participant level.')

    tsv_split_subparser.add_argument(
        "merged_tsv",
        help="Path to the file obtained by the command clinica iotools merge-tsv.",
        type=str)
    tsv_split_subparser.add_argument(
        "formatted_data_path",
        help="Path to the folder containing data extracted by clinicadl tsvtool getlabels.",
        type=str)

    # Optional arguments
    tsv_split_subparser.add_argument(
        "--n_test",
        help="If > 1, number of subjects to put in set with name 'subset_name'. "
             "If < 1, proportion of subjects to put set with name 'subset_name'. "
             "If 0, no training set is created and the whole dataset is considered as one set with name 'subset_name.",
        type=float, default=100.)
    tsv_split_subparser.add_argument(
        "--age_name",
        help="Name of the variable related to the age in the merged_tsv file.",
        type=str, default="age_bl")
    tsv_split_subparser.add_argument(
        "--MCI_sub_categories",
        help="Deactivate default managing of MCI sub-categories to avoid data leakage.",
        action="store_false", default=True)
    tsv_split_subparser.add_argument(
        "--t_val_threshold", "-t",
        help="The threshold used for the chi2 test on sex distributions.",
        default=0.0642, type=float)
    tsv_split_subparser.add_argument(
        "--p_val_threshold", "-p",
        help="The threshold used for the T-test on age distributions.",
        default=0.80, type=float)
    tsv_split_subparser.add_argument(
        "--subset_name",
        help="Name of the subset that is complementary to train.",
        type=str, default="test")

    tsv_split_subparser.set_defaults(func=tsv_split_func)

    tsv_kfold_subparser = tsv_subparser.add_parser(
        'kfold',
        help='Performs a k-fold split on participant level.')

    tsv_kfold_subparser.add_argument(
        "formatted_data_path",
        help="Path to the folder containing data extracted by clinicadl tsvtool getlabels.",
        type=str)

    # Optional arguments
    tsv_kfold_subparser.add_argument(
        "--n_splits",
        help="Number of folds in the k-fold split."
             "If 0, there is no training set and the whole dataset is considered as a test set.",
        type=int, default=5)
    tsv_kfold_subparser.add_argument(
        "--MCI_sub_categories",
        help="Deactivate default managing of MCI sub-categories to avoid data leakage.",
        action="store_false", default=True)
    tsv_kfold_subparser.add_argument(
        "--subset_name",
        help="Name of the subset that is complementary to train.",
        type=str, default="validation")

    tsv_kfold_subparser.set_defaults(func=tsv_kfold_func)

    tsv_analysis_subparser = tsv_subparser.add_parser(
        'analysis',
        help='Produces a demographic analysis of the extracted labels.')

    tsv_analysis_subparser.add_argument(
        "merged_tsv",
        help="Path to the file obtained by the command clinica iotools merge-tsv.",
        type=str)
    tsv_analysis_subparser.add_argument(
        "formatted_data_path",
        help="Path to the folder containing data extracted by clinicadl tsvtool getlabels.",
        type=str)
    tsv_analysis_subparser.add_argument(
        "results_path",
        help="Path to the output tsv file (filename included).",
        type=str)

    # Modality selection
    tsv_analysis_subparser.add_argument(
        "--diagnoses",
        help="Labels selected for the demographic analysis.",
        default=['AD', 'CN'], nargs="+", type=str, choices=['AD', 'CN', 'MCI', 'sMCI', 'pMCI'])
    tsv_analysis_subparser.add_argument(
        "--mmse_name",
        help="Name of the variable related to the MMSE score in the merged_tsv file.",
        type=str, default="MMS")
    tsv_analysis_subparser.add_argument(
        "--age_name",
        help="Name of the variable related to the age in the merged_tsv file.",
        type=str, default="age_bl")
    tsv_analysis_subparser.add_argument(
        "--baseline",
        help="Performs the analysis based on <label>_baseline.tsv files",
        default=False, action="store_true")

    tsv_analysis_subparser.set_defaults(func=tsv_analysis_func)

    return parser
