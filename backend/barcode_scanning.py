from backend.models import Batch

def process_scanned_barcode(scanned_code):
    scanned_code = scanned_code.strip()
    print(f"Processing scanned barcode: '{scanned_code}'") 
    
    batch = Batch.get_batch_by_barcode(scanned_code)

    if batch:
        print(f"Batch Found: {batch}") 
        return batch  
    else:
        print(f"Barcode '{scanned_code}' was not found in the database!") 
        return None  
