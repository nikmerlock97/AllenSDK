from marshmallow import Schema, fields, RAISE
import numpy as np


STYPE_DICT = {fields.Float: 'float', fields.Int: 'int',
              fields.String: 'text', fields.List: 'text',
              fields.DateTime: 'text', fields.UUID: 'text'}
TYPE_DICT = {fields.Float: float, fields.Int: int, fields.String: str,
             fields.List: np.ndarray, fields.DateTime: str, fields.UUID: str}


class RaisingSchema(Schema):
    class Meta:
        unknown = RAISE


class SubjectMetadataSchema(RaisingSchema):
    """This schema contains metadata pertaining to a subject in either a
    behavior or behavior + ophys experiment.
    """

    neurodata_type = 'BehaviorSubject'
    neurodata_type_inc = 'Subject'
    neurodata_doc = "Metadata for an AIBS behavior or behavior + ophys subject"
    # Fields to skip converting to extension
    # In this case they already exist in the 'Subject' builtin pyNWB class
    neurodata_skip = {"age", "genotype", "sex", "subject_id"}

    age = fields.String(
        doc='Age of the specimen donor/subject',
        required=True,
    )
    driver_line = fields.List(
        fields.String,
        doc="Driver line of subject",
        required=True,
        shape=(None,),
    )
    # 'full_genotype' will be stored in pynwb Subject 'genotype' attr
    genotype = fields.String(
        doc='full genotype of subject',
        required=True,
    )
    # 'LabTracks_ID' will be stored in pynwb Subject 'subject_id' attr
    subject_id = fields.Int(
        doc='LabTracks ID of subject',
        required=True,
    )
    reporter_line = fields.List(
        fields.String,
        doc="Reporter line of subject",
        required=True,
        shape=(None,),
    )
    sex = fields.String(
        doc='Sex of the specimen donor/subject',
        required=True,
    )


class BehaviorMetadataSchema(RaisingSchema):
    """This schema contains metadata pertaining to behavior.
    """

    behavior_session_uuid = fields.UUID(
        doc='MTrain record for session, also called foraging_id',
        required=True,
    )
    stimulus_frame_rate = fields.Float(
        doc=('Frame rate (frames/second) of the '
             'visual_stimulus from the monitor'),
        required=True,
    )


class NwbOphysMetadataSchema(RaisingSchema):
    """This schema contains fields that will be stored in pyNWB base classes
    pertaining to optical physiology."""
    # 'emission_lambda' will be stored in
    # pyNWB OpticalChannel 'emission_lambda' attr
    emission_lambda = fields.Float(
        doc='Emission lambda of fluorescent indicator',
        required=True,
    )
    # 'excitation_lambda' will be stored in the pyNWB ImagingPlane
    # 'excitation_lambda' attr
    excitation_lambda = fields.Float(
        doc='Excitation lambda of fluorescent indicator',
        required=True,
    )
    # 'indicator' will be stored in the pyNWB ImagingPlane 'indicator' attr
    indicator = fields.String(
        doc='Name of optical physiology fluorescent indicator',
        required=True,
    )
    # 'targeted_structure' will be stored in the pyNWB
    # ImagingPlane 'location' attr
    targeted_structure = fields.String(
        doc='Anatomical structure targeted for two-photon acquisition',
        required=True,
    )
    # 'ophys_frame_rate' will  be stored in the pyNWB ImagingPlane
    # 'imaging_rate' attr
    ophys_frame_rate = fields.Float(
        doc='Frame rate (frames/second) of the two-photon microscope',
        required=True,
    )


class OphysMetadataSchema(NwbOphysMetadataSchema):
    """This schema contains metadata pertaining to optical physiology (ophys).
    """
    experiment_container_id = fields.Int(
        doc='Container ID for the container that contains this ophys session',
        required=True,
    )
    imaging_depth = fields.Int(
        doc=('Depth (microns) below the cortical surface '
             'targeted for two-photon acquisition'),
        required=True,
    )
    ophys_experiment_id = fields.Int(
        doc='Id for this ophys session',
        required=True,
    )
    rig_name = fields.String(
        doc='Name of optical physiology experiment rig',
        required=True,
    )
    field_of_view_width = fields.Int(
        doc='Width of optical physiology imaging plane in pixels',
        required=True,
    )
    field_of_view_height = fields.Int(
        doc='Height of optical physiology imaging plane in pixels',
        required=True,
    )


class OphysBehaviorMetadataSchema(BehaviorMetadataSchema, OphysMetadataSchema):
    """ This schema contains fields pertaining to ophys+behavior. It is used
    as a template for generating our custom NWB behavior + ophys extension.
    """

    neurodata_type = 'OphysBehaviorMetadata'
    neurodata_type_inc = 'LabMetaData'
    neurodata_doc = "Metadata for behavior + ophys experiments"
    # Fields to skip converting to extension
    # They already exist as attributes for the following pyNWB classes:
    # OpticalChannel, ImagingPlane, NWBFile
    neurodata_skip = {"emission_lambda", "excitation_lambda", "indicator",
                      "targeted_structure", "experiment_datetime",
                      "ophys_frame_rate"}

    session_type = fields.String(
        doc='Experimental session description',
        allow_none=True,
        required=True,
    )
    # 'experiment_datetime' will be stored in
    # pynwb NWBFile 'session_start_time' attr
    experiment_datetime = fields.DateTime(
        doc='Date of the experiment (UTC, as string)',
        required=True,
    )


class CompleteOphysBehaviorMetadataSchema(OphysBehaviorMetadataSchema,
                                          SubjectMetadataSchema):
    """This schema combines fields from behavior, ophys, and subject schemas.
    Metadata info is passed by the behavior+ophys session in a combined lump
    containing all the field types.
    """
    pass


class BehaviorTaskParametersSchema(RaisingSchema):
    """This schema encompasses task parameters used for behavior or
    ophys + behavior.
    """
    neurodata_type = 'BehaviorTaskParameters'
    neurodata_type_inc = 'LabMetaData'
    neurodata_doc = "Metadata for behavior or behavior + ophys task parameters"

    blank_duration_sec = fields.List(
        fields.Float,
        doc=('The lower and upper bound (in seconds) for a randomly chosen '
             'inter-stimulus interval duration for a trial'),
        required=True,
        shape=(2,),
    )
    stimulus_duration_sec = fields.Float(
        doc='Duration of each stimulus presentation in seconds',
        required=True,
    )
    omitted_flash_fraction = fields.Float(
        doc='Fraction of flashes/image presentations that were omitted',
        required=True,
        allow_nan=True,
    )
    response_window_sec = fields.List(
        fields.Float,
        doc=('The lower and upper bound (in seconds) for a randomly chosen '
             'time window where subject response influences trial outcome'),
        required=True,
        shape=(2,),
    )
    reward_volume = fields.Float(
        doc='Volume of water (in mL) delivered as reward',
        required=True,
    )
    stage = fields.String(
        doc='Stage of behavioral task',
        required=True,
    )
    stimulus = fields.String(
        doc='Stimulus type',
        required=True,
    )
    stimulus_distribution = fields.String(
        doc=("Distribution type of drawing change times "
             "(e.g. 'geometric', 'exponential')"),
        required=True,
    )
    task = fields.String(
        doc='The name of the behavioral task',
        required=True,
    )
    n_stimulus_frames = fields.Int(
        doc='Total number of stimuli frames',
        required=True,
    )
