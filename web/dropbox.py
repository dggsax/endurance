from web import dbx
from web.models import Member
from web.models.member import AffiliationEnum

def dropbox_setup_member(member):
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
    assert isinstance(member, Member), "Instance of `model.Member` must be provided to this method"
    
    path = generate_path(member)

    file_request_url = create_file_request(member, path)
    folder_url = create_shared_link(path)
    
    member.dropbox_file_upload_url = file_request_url
    member.dropbox_shared_folder_url = folder_url

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
        path = F"/submissions/{member.class_year}/{member.full_name_for_path()}"
    else:
        path = F"/submissions/Other/{member.full_name_for_path()}"

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

    title = F"Endurance File Request for {member.full_name_for_path()}"
    
    result = dbx.file_requests_create(title, path)

    return result.url

def create_shared_link(path):
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

    return result.url