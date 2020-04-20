from web import dbx, db
from web.models import Member
from web.models.member import AffiliationEnum

from dropbox.exceptions import ApiError


def dropbox_setup_member(member, commit=False):
    """
    setup_member generate dropbox links for submitted Member 
        and add them to instance
    
    :param member: [description]
    :type member: [type]
    :return: two URLs, the first being a URL for the user's
        custom file request link and the second being a URL
        to the folder that will store their files
    :rtype: tuple
    """
    assert isinstance(
        member, Member
    ), "Instance of `model.Member` must be provided to this method"

    path = generate_path(member)

    create_file_request(member, path)
    create_shared_link(member, path)

    if commit:
        db.session.commit()


def cancel_request(member, commit=True):
    """
    cancel_request Cancel request by deleting the folder generated for the user
    
    :param member: member
    :type member: web.models.Member
    :param commit: whether or not to commit changes to database session, defaults 
        to True
    :type commit: bool, optional
    :raises e: We expect ApiError in case the folder doesn't exist and the file
        request was already deleted for that user, but if we have another exception,
        we want to be sure to raise it
    """

    try:
        dbx.files_delete(path=generate_path(member))
    except ApiError as e:
        pass
    except Exception as e:
        raise e

    member.dropbox_file_request_id = None
    member.dropbox_file_upload_url = None
    member.dropbox_shared_folder_url = None

    if commit:
        db.session.commit()

def generate_path(member):
    """
    generate_path generate file path for member based 
        on affiliation status. If Alumni/Student, then
        generate path based on class year and name. 
        Otherwise, use generic "Other" path and check 
        for duplicate names
    
    :param member: [description]
    :type member: [type]
    """

    if member.affiliation is AffiliationEnum.StudentOrAlumni:
        path = f"/submissions/{member.class_year}/{member.full_name_for_path()} - {member.email}"
    else:
        path = f"/submissions/Other/{member.full_name_for_path()} - {member.email}"

    return path


def create_file_request(member, path):
    """
    create_file_request given a path for the member, 
        generate a file request unique to them that 
        they can use to upload files
    
    :param member: instance of member, used to generate 
        name for file request title
    :type member: web.models.Member
    :param path: unique folder path for file request
    :type path: string
    :return: url for file_request
    :rtype: string
    """

    title = f"Endurance File Request for {member.full_name_for_path()}"

    result = dbx.file_requests_create(title, path)

    member.dropbox_file_request_id = result.id
    member.dropbox_file_upload_url = result.url


def create_shared_link(member, path):
    """
    create_shared_link generate a sharable link to folder 
        containing files uploaded via the member's file request
        link
    
    :param path: path of folder created for file request
    :type path: string
    :return: url for folder
    :rtype: string
    """

    result = dbx.sharing_create_shared_link(path)

    member.dropbox_shared_folder_url = result.url
